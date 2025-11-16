from datetime import datetime, timedelta
from qs.events_data import EVENTS_DF
from qs.game.player import Player
from qs.prompting import build_state_evaluation_prompt
from qs.server.llm_client import call_llm, call_llm_chat
from qs.server.schemas import ChatMessage


class Chatbot:
    def __init__(self):
        pass

    def get_relevant_events(self, date: datetime) -> list[str]:
        # Retrieve events in the past 4 weeks from the given date
        four_weeks_ago = date - timedelta(weeks=4)
        recent_events = EVENTS_DF[
            (EVENTS_DF["Date"] >= four_weeks_ago.strftime("%Y-%m-%d"))
            & (EVENTS_DF["Date"] <= date.strftime("%Y-%m-%d"))
        ]["Event Title"].tolist()
        return recent_events

    def evaluate_user_state(self, player: Player) -> str:
        player_state = player.dump_player_data()

        prompt = build_state_evaluation_prompt(
            player_state=player_state,
            events=self.get_relevant_events(player.get_session().get_time())
        )

        text = call_llm(
            system_prompt="You are a helpful financial literacy tutor for teenagers.", user_prompt=prompt)
        return text

    def chat(self, player: Player, messages: list[ChatMessage]) -> str:
        messages.insert(0, ChatMessage(
            role="system",
            content=build_state_evaluation_prompt(
                player_state=player.dump_player_data(),
                events=self.get_relevant_events(
                    player.get_session().get_time())
            )
        ))
        response = call_llm_chat(messages)
        return response
