import pandas as pd
import numpy as np

from src.technical_indicators import TechnicalIndicators
from src.strategy_signals import generate_signals


def make_series(n=200, seed=42):
    np.random.seed(seed)
    base = 100.0
    closes = base + np.cumsum(np.random.randn(n) * 0.5)
    highs = closes + np.random.rand(n) * 0.5
    lows = closes - np.random.rand(n) * 0.5
    df = pd.DataFrame({'open': closes, 'high': highs, 'low': lows, 'close': closes})
    return df


def test_macd_basic():
    df = make_series(100)
    macd_df = TechnicalIndicators.macd(df['close'])
    assert 'macd' in macd_df.columns
    assert 'signal' in macd_df.columns
    assert 'hist' in macd_df.columns
    # macd should be finite
    assert pd.notnull(macd_df['macd'].iloc[-1])


def test_fibonacci_levels():
    df = make_series(150)
    fib = TechnicalIndicators.fibonacci_retracement(df, lookback=50)
    assert 'high' in fib and 'low' in fib and 'levels' in fib
    assert fib['high'] >= fib['low']
    # levels include common ratios
    for r in [0.236, 0.382, 0.5, 0.618]:
        assert r in fib['levels']


def test_generate_signals_runs():
    df = make_series(200)
    sig = generate_signals(df)
    assert 'recommendation' in sig
    assert sig['recommendation'] in ('BUY', 'SELL', 'HOLD') or 'error' in sig
