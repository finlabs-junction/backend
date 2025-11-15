from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, date, timedelta

import yfinance as yf

from qs.cache import lru_cache


executor = ThreadPoolExecutor(max_workers=1)


def fetch_stock_prices(
    symbols: tuple[str, ...], 
    start_time: datetime, 
    end_time: datetime,
):
    start_time -= timedelta(days=14)
    end_time += timedelta(days=1)

    start_day = start_time.strftime("%Y-%m-%d")
    end_day = end_time.strftime("%Y-%m-%d")
    return yf.download(
        symbols, 
        start=start_day, 
        end=end_day,
        progress=False,
        auto_adjust=True,
        group_by="ticker",
    )


@lru_cache(maxsize=16)
async def get_stock_prices(
    symbols: tuple[str, ...], 
    period: tuple[datetime, datetime],
):
    start_time, end_time = period

    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(
        executor,
        fetch_stock_prices,
        symbols,
        start_time,
        end_time,
    )

    assert df is not None

    out: dict[str, dict[date, float]] = {}

    for sym in symbols:
        if sym not in df:
            out[sym] = {}
            continue
        
        sub = df[sym].dropna()
        if sub.empty:
            out[sym] = {}
            continue

        sub["avg"] = (sub["High"] + sub["Low"]) / 2

        out[sym] = {
            idx.date(): float(row["avg"])
            for idx, row in sub.iterrows()
        }

    return out
