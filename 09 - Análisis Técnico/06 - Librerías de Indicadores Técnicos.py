# -*- coding: utf-8 -*-
# Importar librerías
import pandas as pd
import numpy as np

# Intentar importar pandas_ta y ta, si no están disponibles usar fallbacks
pd_ta = None
ta = None

try:
    import pandas_ta as pd_ta_lib  # pip install pandas-ta
    pd_ta = pd_ta_lib
except Exception:
    pd_ta = None
    print("Aviso: pandas_ta no está disponible. Se usarán fallbacks con pandas/ta si es posible.")

try:
    import ta as ta_lib  # pip install ta
    ta = ta_lib
except Exception:
    ta = None
    print("Aviso: la librería 'ta' no está disponible. Se usarán implementaciones alternativas cuando sea posible.")

# Obtener datos
df = pd.read_csv("../datos/AMZN.csv", index_col="Date", parse_dates=True)

# --- Indicadores: MA / EMA ---
# Intentar usar pandas_ta, si falla usar alternativas con pandas
try:
    if pd_ta is not None:
        try:
            ma = pd_ta.sma(df["Close"], length=8)
        except Exception:
            # algunas versiones usan pd_ta.overlap.sma
            try:
                ma = pd_ta.overlap.sma(df["Close"], length=8)
            except Exception:
                ma = df["Close"].rolling(window=8).mean()
        try:
            ema = pd_ta.ema(df["Close"], length=14)
        except Exception:
            try:
                ema = pd_ta.overlap.ema(df["Close"], length=14)
            except Exception:
                ema = df["Close"].ewm(span=14, adjust=False).mean()
    else:
        raise ImportError
except ImportError:
    ma = df["Close"].rolling(window=8).mean()
    ema = df["Close"].ewm(span=14, adjust=False).mean()

# --- Indicador: CCI ---
try:
    if pd_ta is not None:
        try:
            cci = pd_ta.momentum.cci(high=df["High"], low=df["Low"], close=df["Close"], length=14)
        except Exception:
            # fallback a función top-level si aplica
            cci = pd_ta.cci(high=df["High"], low=df["Low"], close=df["Close"], length=14)
    elif ta is not None:
        from ta.trend import CCIIndicator
n        cci = CCIIndicator(high=df["High"], low=df["Low"], close=df["Close"], window=14).cci()
    else:
        # Implementación simple de CCI (no exacta a pandas_ta, pero funcional)
        tp = (df["High"] + df["Low"] + df["Close"]) / 3
        ma_tp = tp.rolling(window=14).mean()
        mad = tp.rolling(window=14).apply(lambda x: np.fabs(x - x.mean()).mean())
        cci = (tp - ma_tp) / (0.015 * mad)
except Exception:
    # En caso de cualquier fallo, rellenar con NaN
    cci = pd.Series(np.nan, index=df.index)

# --- Indicador: ATR ---
try:
    if pd_ta is not None:
        try:
            atr = pd_ta.atr(high=df["High"], low=df["Low"], close=df["Close"], length=21)
        except Exception:
            atr = pd_ta.volatility.atr(high=df["High"], low=df["Low"], close=df["Close"], length=21)
    elif ta is not None:
        from ta.volatility import AverageTrueRange
n        atr = AverageTrueRange(high=df["High"], low=df["Low"], close=df["Close"], window=21).average_true_range()
    else:
        high = df["High"]
        low = df["Low"]
        prev_close = df["Close"].shift(1)
        tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
        atr = tr.rolling(window=21, min_periods=1).mean()
except Exception:
    atr = pd.Series(np.nan, index=df.index)

# --- Indicadores con la librería 'ta' (RSI, MACD, CMF) ---
# RSI
try:
    if ta is not None:
        rsi = ta.momentum.RSIIndicator(close=df["Close"], window=14).rsi()
    elif pd_ta is not None:
        rsi = pd_ta.momentum.rsi(df["Close"], length=14)
    else:
        # Implementación RSI simple (Wilder's EMA)
        window = 14
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/window, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/window, adjust=False).mean()
        rs = avg_gain / (avg_loss.replace(0, np.nan))
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.fillna(0)
except Exception:
    rsi = pd.Series(np.nan, index=df.index)

# MACD
try:
    if ta is not None:
        macd = ta.trend.MACD(close=df["Close"], window_slow=26, window_fast=12, window_sign=9).macd()
    elif pd_ta is not None:
        # pandas_ta macd devuelve un DataFrame con macd, macd_signal, macd_hist
        macd_df = pd_ta.macd(df["Close"], fast=12, slow=26, signal=9)
        # intentar extraer la columna macd
        if isinstance(macd_df, pd.DataFrame):
            # nombres comunes: MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
            col_candidates = [c for c in macd_df.columns if "MACD" in c.upper() or "macd" in c.lower()]
            if col_candidates:
                macd = macd_df[col_candidates[0]]
            else:
                macd = macd_df.iloc[:, 0]
        else:
            macd = macd_df
    else:
        ema_fast = df["Close"].ewm(span=12, adjust=False).mean()
        ema_slow = df["Close"].ewm(span=26, adjust=False).mean()
        macd = ema_fast - ema_slow
except Exception:
    macd = pd.Series(np.nan, index=df.index)

# CMF (Chaikin Money Flow)
try:
    if ta is not None:
        cmf = ta.volume.ChaikinMoneyFlowIndicator(high=df["High"], low=df["Low"], close=df["Close"], volume=df["Volume"]).chaikin_money_flow()
    elif pd_ta is not None:
        cmf = pd_ta.cmf(high=df["High"], low=df["Low"], close=df["Close"], volume=df["Volume"], length=20)
    else:
        n = 20
        high = df["High"]
        low = df["Low"]
        close = df["Close"]
        vol = df["Volume"]
        denom = (high - low).replace(0, np.nan)
        mfm = ((close - low) - (high - close)) / denom
        mfv = mfm * vol
        cmf = mfv.rolling(window=n, min_periods=1).sum() / vol.rolling(window=n, min_periods=1).sum()
        cmf = cmf.fillna(0)
except Exception:
    cmf = pd.Series(np.nan, index=df.index)

# Mostrar resumen rápido
print("Indicadores calculados: ma/ema/cci/atr/rsi/macd/cmf. Últimos valores:")
print("MA:", ma.iloc[-1] if hasattr(ma, 'iloc') else ma)
print("EMA:", ema.iloc[-1] if hasattr(ema, 'iloc') else ema)
print("CCI:", cci.iloc[-1] if hasattr(cci, 'iloc') else cci)
print("ATR:", atr.iloc[-1] if hasattr(atr, 'iloc') else atr)
print("RSI:", rsi.iloc[-1] if hasattr(rsi, 'iloc') else rsi)
print("MACD:", macd.iloc[-1] if hasattr(macd, 'iloc') else macd)
print("CMF:", cmf.iloc[-1] if hasattr(cmf, 'iloc') else cmf)
