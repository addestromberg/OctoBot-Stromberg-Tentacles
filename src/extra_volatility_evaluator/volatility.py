#  Drakkar-Software OctoBot-Tentacles
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import tulipy

import octobot_commons.constants as commons_constants
import octobot_commons.enums as enums
import octobot_commons.data_util as data_util
import octobot_evaluators.evaluators as evaluators
import octobot_evaluators.util as evaluators_util
import octobot_trading.api as trading_api


class ATRVolatilityEvaluator(evaluators.TAEvaluator):
    ATR_PERIOD = "atr_period"

    def __init__(self, tentacles_setup_config):
        super().__init__(tentacles_setup_config)
        self.atr_period = 14

    def init_user_inputs(self, inputs: dict) -> None:
        self.period = self.UI.user_input(
            self.ATR_PERIOD,
            enums.UserInputTypes.INT,
            self.atr_period,
            inputs,
            min_val=2,
            title="Period: length of the stochastic RSI period.",
        )

    async def ohlcv_callback(
        self,
        exchange: str,
        exchange_id: str,
        cryptocurrency: str,
        symbol: str,
        time_frame,
        candle,
        inc_in_construction_data,
    ):
        exchange_symbol_data = self.get_exchange_symbol_data(exchange, exchange_id, symbol)
        high = trading_api.get_symbol_high_candles(
            exchange_symbol_data, time_frame, include_in_construction=inc_in_construction_data
        )
        low = trading_api.get_symbol_low_candles(
            exchange_symbol_data, time_frame, include_in_construction=inc_in_construction_data
        )
        close = trading_api.get_symbol_close_candles(
            exchange_symbol_data, time_frame, include_in_construction=inc_in_construction_data
        )
        self.eval_note = commons_constants.START_PENDING_EVAL_NOTE
        if len(close) > self.atr_period:
            await self.evaluate(cryptocurrency, symbol, time_frame, candle, high, low, close)
        await self.evaluation_completed(
            cryptocurrency,
            symbol,
            time_frame,
            eval_time=evaluators_util.get_eval_time(full_candle=candle, time_frame=time_frame),
        )

        await self.evaluate(cryptocurrency, symbol, time_frame, high, low, close, candle)

    async def evaluate(self, cryptocurrency, symbol, time_frame, high, low, close, candle):
        try:
            if isinstance(self.period, (int, float)) and len(close) >= self.period:
                high = data_util.drop_nan(high)
                low = data_util.drop_nan(low)
                close = data_util.drop_nan(close)
                atr = tulipy.atr(high, low, close, self.atr_period)[-1]
                self.logger.debug(f"Calculated ATR: {atr}")
                self.eval_note = float(atr)
        except Exception as e:
            self.logger.error("[ATR Evaluator] Failed to calculate ATR.")
            self.logger.debug(str(e))
            self.eval_note = commons_constants.START_PENDING_EVAL_NOTE

        await self.evaluation_completed(
            cryptocurrency,
            symbol,
            time_frame,
            eval_time=evaluators_util.get_eval_time(full_candle=candle, time_frame=time_frame),
        )
