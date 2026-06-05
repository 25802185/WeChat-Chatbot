import pytest
from emotion import has_emoji, get_emoji_for_emotion


def test_has_emoji_with_emoji():
    assert has_emoji("你好呀😊") == True
    assert has_emoji("爱你💕🥰") == True


def test_has_emoji_without_emoji():
    assert has_emoji("你好呀") == False
    assert has_emoji("今天天气真好") == False


def test_get_emoji_for_emotion_happy():
    emoji = get_emoji_for_emotion("开心")
    assert emoji in ["😊", "😄", "💖", "✨"]


def test_get_emoji_for_emotion_sad():
    emoji = get_emoji_for_emotion("难过")
    assert emoji in ["🥺", "😢", "💔"]


def test_get_emoji_for_emotion_neutral():
    emoji = get_emoji_for_emotion("neutral")
    assert emoji is None
