"""Simple strategy signal helpers combining MACD and Fibonacci retracement

This module provides a conservative example of how to use MACD and Fibonacci
retracement levels to generate entry suggestions. It is intentionally simple so
it is easy to review and test before integrating into `main` or `chatgpt_advisor`.
"""
from typing import Dict, Any
import pandas as pd
from .technical_indicators import TechnicalIndicators
from . import config


def price_near_level(price: float, level: float, tol: float = 0.0025) -> bool:
    """Return True if price is within tol (fraction) of level."""
    if level is None:
        return False
    return abs(price - level) / max(level, 1e-8) <= tol


def generate_signals(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate combined signals using MA, RSI, ATR, MACD and Fibonacci.

    Args:
        df: DataFrame with columns ['open','high','low','close'] indexed by time.

    Returns:
        dict: { 'trend': 'up'|'down'|'flat', 'macd': {...}, 'fib': {...}, 'recommendation': 'BUY'|'SELL'|'HOLD', 'entry': price, 'stop': price }
    """
    results = {}

    # Basic checks
    if len(df) < 10:
        return {'error': 'insufficient data'}

    close = df['close']
    last_price = float(close.iloc[-1])

    # MA-based trend: short MA vs long MA
    ma_short = TechnicalIndicators.calculate_ma(df, period=config.MA_PERIOD)
    ma_long = TechnicalIndicators.calculate_ma(df, period=max(2 * config.MA_PERIOD, config.MA_PERIOD + 1))
    ma_s = ma_short.iloc[-1]
    ma_l = ma_long.iloc[-1]

    trend = 'flat'
    if ma_s > ma_l:
        trend = 'up'
    elif ma_s < ma_l:
        trend = 'down'

    results['trend'] = trend

    # MACD
    macd_df = TechnicalIndicators.macd(close, fast=config.MACD_FAST, slow=config.MACD_SLOW, signal=config.MACD_SIGNAL)
    macd_last = macd_df.iloc[-1]
    macd_prev = macd_df.iloc[-2]
    macd_signal = 'neutral'
    # detect cross
    if macd_prev['macd'] <= macd_prev['signal'] and macd_last['macd'] > macd_last['signal']:
        macd_signal = 'bullish_cross'
    elif macd_prev['macd'] >= macd_prev['signal'] and macd_last['macd'] < macd_last['signal']:
        macd_signal = 'bearish_cross'

    results['macd'] = {
        'macd': float(macd_last['macd']),
        'signal': float(macd_last['signal']),
        'hist': float(macd_last['hist']),
        'cross': macd_signal
    }

    # Fibonacci
    fib = TechnicalIndicators.fibonacci_retracement(df, lookback=config.FIB_LOOKBACK)
    results['fib'] = fib

    # Check if price is near any common retracement levels (38.2, 50, 61.8)
    candidates = [0.382, 0.5, 0.618]
    hit_level = None
    for r in candidates:
        lvl = fib['levels'].get(r)
        if price_near_level(last_price, lvl, tol=0.005):
            hit_level = {'ratio': r, 'price': lvl}
            break

    results['fib_hit'] = hit_level

    # Combine rules for a conservative recommendation
    recommendation = 'HOLD'
    entry = None
    stop = None

    # Example BUY rule: uptrend + fib pullback hit + MACD bullish cross
    if trend == 'up' and hit_level and macd_signal == 'bullish_cross':
        recommendation = 'BUY'
        entry = last_price
        # stop below next lower fib level or use ATR-based stop
        stop = fib['levels'].get(0.618, last_price * (1 - 0.02))

    # Example SELL rule: downtrend + fib pullback hit + MACD bearish cross
    if trend == 'down' and hit_level and macd_signal == 'bearish_cross':
        recommendation = 'SELL'
        entry = last_price
        stop = fib['levels'].get(0.618, last_price * (1 + 0.02))

    results['recommendation'] = recommendation
    results['entry'] = entry
    results['stop'] = stop

    return results


if __name__ == '__main__':
    # Quick demonstration using TechnicalIndicators' sample data
    import numpy as np
    import pandas as pd
    dates = pd.date_range('2024-01-01', periods=200, freq='1H')
    base = 40000
    df = pd.DataFrame({
        'open': base + np.cumsum(np.random.randn(200) * 50),
        'high': base + np.cumsum(np.random.randn(200) * 60),
        'low': base + np.cumsum(np.random.randn(200) * 60),
        'close': base + np.cumsum(np.random.randn(200) * 50),
    }, index=dates)

    sig = generate_signals(df)
    print(sig)
