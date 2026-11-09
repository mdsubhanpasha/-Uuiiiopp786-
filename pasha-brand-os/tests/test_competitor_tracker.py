from unittest import mock

import app.competitor_tracker as ct
from app.competitor_tracker import CompetitorTracker


def _write_config(tmp_path, body):
    path = tmp_path / "config.yaml"
    path.write_text(body)
    return str(path)


def test_influencers_accept_plain_names_and_profile_urls(tmp_path):
    cfg = _write_config(tmp_path, (
        "influencers:\n"
        "  - \"Plain Name\"\n"
        "  - name: \"With Url\"\n"
        "    url: \"https://www.linkedin.com/in/with-url\"\n"
    ))
    tracker = CompetitorTracker(config_path=cfg)
    assert tracker.influencers == ["Plain Name", "With Url"]
    assert tracker.profile_urls == ["https://www.linkedin.com/in/with-url"]


def test_scrape_posts_profile_urls_and_maps_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("APIFY_API_TOKEN", "dummy")
    cfg = _write_config(tmp_path, (
        "influencers:\n"
        "  - \"Name Only\"\n"
        "  - name: \"Jane Doe\"\n"
        "    url: \"https://www.linkedin.com/in/janedoe\"\n"
    ))
    tracker = CompetitorTracker(config_path=cfg)

    response = mock.Mock(status_code=201)
    response.json.return_value = [
        {"authorName": "Jane Doe", "text": "Hook line here\n\nBody of the post.", "numLikes": 4321},
        {"error_message": "Profile not found", "error_type": "not_found", "sourceUrl": "https://www.linkedin.com/in/x"},
    ]
    with mock.patch.object(ct.requests, "post", return_value=response) as post:
        hooks = tracker.scrape_and_analyze_hooks()

    url = post.call_args.args[0]
    assert "/acts/johnvc~linkedin-posts-api/run-sync-get-dataset-items" in url
    assert post.call_args.kwargs["json"] == {
        "profileUrls": ["https://www.linkedin.com/in/janedoe"],
        "maxPostsPerProfile": 3,
    }
    assert hooks == [{
        "influencer_name": "Jane Doe",
        "original_post": "Hook line here\n\nBody of the post.",
        "hook_type": "Data-Driven",
        "hook_text": "Hook line here",
        "likes": 4321,
    }]


def test_no_profile_urls_skips_api_and_uses_fallback(tmp_path, monkeypatch):
    monkeypatch.setenv("APIFY_API_TOKEN", "dummy")
    cfg = _write_config(tmp_path, "influencers:\n  - \"Name Only\"\n")
    tracker = CompetitorTracker(config_path=cfg)
    with mock.patch.object(ct.requests, "post") as post:
        hooks = tracker.scrape_and_analyze_hooks()
    post.assert_not_called()
    assert [h["influencer_name"] for h in hooks] == ["Name Only"]
