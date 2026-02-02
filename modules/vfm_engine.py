"""
VFM Engine: LSTM + MLP Hybrid
- LSTM: 시계열 가격 예측 (6개월 후)
- MLP: 정적 인프라 기반 입지 가치 평가
- VFM Index = α × (MLP / 100) + β × (LSTM Future / Current)
"""

import os
import pickle
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from typing import Dict, Tuple, Optional

# TensorFlow/Keras 임포트
try:
    from tensorflow import keras
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    print("⚠️ TensorFlow를 설치하세요: pip install tensorflow")


class VFMMLP(nn.Module):
    """PyTorch MLP for location value assessment"""

    def __init__(self, input_dim=5):
        super(VFMMLP, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 16)
        self.fc4 = nn.Linear(16, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x


class VFMEngine:
    """
    VFM 추론 엔진 (LSTM + MLP)
    - LSTM: 시계열 가격 예측
    - MLP: 입지 가치 평가
    - VFM Index 계산
    """

    def __init__(
        self,
        lstm_model_path: str,
        lstm_scaler_X_path: str,
        lstm_scaler_y_path: str,
        mlp_checkpoint_path: Optional[str] = None,
        mlp_scaler_path: Optional[str] = None,
        use_mlp: bool = True,
        alpha: float = 0.6,
        beta: float = 0.4
    ):
        self.use_mlp = use_mlp
        self.alpha = alpha
        self.beta = beta

        # LSTM 모델 로드
        if KERAS_AVAILABLE and os.path.exists(lstm_model_path):
            self.lstm_model = keras.models.load_model(lstm_model_path)
            print(f"✅ LSTM 모델 로드: {lstm_model_path}")
        else:
            self.lstm_model = None
            print(f"⚠️ LSTM 모델을 찾을 수 없음: {lstm_model_path}")

        # LSTM 스케일러 로드
        if os.path.exists(lstm_scaler_X_path):
            with open(lstm_scaler_X_path, 'rb') as f:
                self.lstm_scaler_X = pickle.load(f)
            print(f"✅ LSTM X 스케일러 로드")
        else:
            self.lstm_scaler_X = None
            print(f"⚠️ LSTM X 스케일러를 찾을 수 없음")

        if os.path.exists(lstm_scaler_y_path):
            with open(lstm_scaler_y_path, 'rb') as f:
                self.lstm_scaler_y = pickle.load(f)
            print(f"✅ LSTM y 스케일러 로드")
        else:
            self.lstm_scaler_y = None
            print(f"⚠️ LSTM y 스케일러를 찾을 수 없음")

        # MLP 모델 로드
        if use_mlp and mlp_checkpoint_path and os.path.exists(mlp_checkpoint_path):
            self.mlp_model = VFMMLP(input_dim=5)
            self.mlp_model.load_state_dict(torch.load(
                mlp_checkpoint_path, map_location='cpu'))
            self.mlp_model.eval()
            print(f"✅ MLP 모델 로드: {mlp_checkpoint_path}")

            with open(mlp_scaler_path, 'rb') as f:
                self.mlp_scaler = pickle.load(f)
            print(f"✅ MLP 스케일러 로드")
        else:
            self.mlp_model = None
            self.mlp_scaler = None
            print(f"⚠️ MLP 미사용 또는 파일 없음")

        # LSTM 피처
        self.lstm_features = [
            'total_deposit_median', 'trade_count', 'BASE_RATE', 'CPI_YOY',
            'deposit_lag_1', 'deposit_lag_3', 'deposit_lag_6', 'deposit_lag_9',
            'base_rate_lag_3', 'base_rate_lag_6', 'base_rate_lag_9',
            'cpi_yoy_lag_3', 'cpi_yoy_lag_6', 'cpi_yoy_lag_9',
            'base_rate_diff_3'
        ]

        # MLP 피처
        self.mlp_features = [
            'trans_index', 'conv_index', 'env_index',
            'safety_score_scaled', 'grid_crime_index'
        ]

    def predict_lstm(self, df: pd.DataFrame, horizon: int = 6) -> np.ndarray:
        """LSTM으로 미래 가격 예측"""
        if self.lstm_model is None or self.lstm_scaler_X is None or self.lstm_scaler_y is None:
            print("⚠️ LSTM 모델 또는 스케일러 없음")
            return df['total_deposit_median'].values

        try:
            # 피처 추출
            X = df[self.lstm_features].values

            # 스케일링
            X_scaled = self.lstm_scaler_X.transform(X)

            # LSTM 입력 형태로 변환 (samples, timesteps, features)
            X_reshaped = X_scaled.reshape(
                X_scaled.shape[0], 1, X_scaled.shape[1])

            # 예측
            y_pred_scaled = self.lstm_model.predict(X_reshaped, verbose=0)

            # 역스케일링
            y_pred = self.lstm_scaler_y.inverse_transform(y_pred_scaled)

            # horizon에 따른 컬럼 선택 (3m=0, 6m=1, 9m=2, 12m=3)
            horizon_map = {3: 0, 6: 1, 9: 2, 12: 3}
            col_idx = horizon_map.get(horizon, 1)

            if y_pred.shape[1] > col_idx:
                return y_pred[:, col_idx]
            else:
                return y_pred[:, 0]

        except Exception as e:
            print(f"⚠️ LSTM 예측 실패: {str(e)}")
            return df['total_deposit_median'].values

    def predict_mlp(self, df: pd.DataFrame) -> np.ndarray:
        """MLP로 입지 가치 평가 (0-100점)"""
        if self.mlp_model is None or self.mlp_scaler is None:
            return np.zeros(len(df))

        try:
            X = df[self.mlp_features].values
            X_scaled = self.mlp_scaler.transform(X)
            X_tensor = torch.FloatTensor(X_scaled)

            with torch.no_grad():
                scores = self.mlp_model(X_tensor).numpy().flatten()

            # 0-100점으로 정규화
            scores = np.clip(scores, 0, 100)
            return scores

        except Exception as e:
            print(f"⚠️ MLP 예측 실패: {str(e)}")
            return np.zeros(len(df))

    def calculate_vfm(
        self,
        df: pd.DataFrame,
        horizon: int = 6
    ) -> pd.DataFrame:
        """
        VFM 지수 계산
        VFM = α × (MLP Score / 100) + β × (LSTM Future / Current Price)
        """
        result = df.copy()

        # LSTM 예측
        future_prices = self.predict_lstm(df, horizon)
        result['future_price'] = future_prices

        # MLP 평가
        if self.use_mlp and self.mlp_model is not None:
            mlp_scores = self.predict_mlp(df)
            result['mlp_score'] = mlp_scores

            # VFM 계산
            current_price = df['total_deposit_median'].values
            price_ratio = future_prices / (current_price + 1e-6)
            mlp_normalized = mlp_scores / 100.0

            result['vfm_index'] = self.alpha * \
                mlp_normalized + self.beta * price_ratio
        else:
            # MLP 미사용 시 가격 변화율만 사용
            current_price = df['total_deposit_median'].values
            result['vfm_index'] = future_prices / (current_price + 1e-6)

        # 상승률 계산
        result['price_change_pct'] = (
            (result['future_price'] - df['total_deposit_median'])
            / (df['total_deposit_median'] + 1e-6) * 100
        )

        result['horizon'] = horizon
        return result


def load_vfm_engine(
    rent_type: str = 'monthly',
    use_mlp: bool = True,
    alpha: float = 0.6,
    beta: float = 0.4
) -> VFMEngine:
    """VFM 엔진 로드 (LSTM + MLP)"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # LSTM 모델 경로
    suffix = '_jeonse' if rent_type == 'jeonse' else ''
    lstm_model_path = os.path.join(
        project_root, 'models', 'lstm',
        f'vfm_lstm_time_split{suffix}_v1.h5'
    )
    lstm_scaler_X_path = os.path.join(
        project_root, 'models', 'lstm',
        f'scaler_X_time{suffix}.pkl'
    )
    lstm_scaler_y_path = os.path.join(
        project_root, 'models', 'lstm',
        f'scaler_y_time{suffix}.pkl'
    )

    # MLP 모델 경로
    mlp_path = os.path.join(
        project_root, 'models', 'model_output2', 'model_colab',
        'vfm_mlp_pytorch.pth'
    )
    mlp_scaler_path = os.path.join(
        project_root, 'models', 'model_output2', 'model_colab',
        'mlp_scaler.pkl'
    )

    return VFMEngine(
        lstm_model_path=lstm_model_path,
        lstm_scaler_X_path=lstm_scaler_X_path,
        lstm_scaler_y_path=lstm_scaler_y_path,
        mlp_checkpoint_path=mlp_path if use_mlp else None,
        mlp_scaler_path=mlp_scaler_path if use_mlp else None,
        use_mlp=use_mlp,
        alpha=alpha,
        beta=beta
    )
