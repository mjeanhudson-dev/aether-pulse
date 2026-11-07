# Update Aether Pulse leaderboard with exact numbers from T3 Code screenshots
import json
import re

with open("aether_pulse_leaderboard.html", "r", encoding="utf-8") as f:
    content = f.read()

# Exact replacement for Cost and Tokens by type
content = re.sub(
    r'Input:\s*<strong>\$11\.20</strong>',
    'Input: <strong>$11.26</strong>',
    content
)
content = re.sub(
    r'Cache read:\s*<strong>\$105\.02</strong>',
    'Cache read: <strong>$135.62</strong>',
    content
)
content = re.sub(
    r'Cache write:\s*<strong>\$129\.38</strong>',
    'Cache write: <strong>$119.58</strong>',
    content
)
content = re.sub(
    r'Output:\s*<strong>\$58\.05</strong>',
    'Output: <strong>$36.05</strong>',
    content
)

content = re.sub(
    r'Input:\s*<strong>133M</strong>',
    'Input: <strong>132M</strong>',
    content
)
content = re.sub(
    r'Cache read:\s*<strong>3\.94B</strong>',
    'Cache read: <strong>2.48B</strong>',
    content
)
content = re.sub(
    r'Cache write:\s*<strong>100\.8M</strong>',
    'Cache write: <strong>34.5M</strong>',
    content
)
content = re.sub(
    r'Output:\s*<strong>29\.3M</strong>',
    'Output: <strong>15.8M</strong>',
    content
)

# Replace Headline totals in 90d to 2.66B, $303.68, $1,975.10 saved
content = re.sub(
    r'"totals":\s*\{\s*"processed":\s*"4\.20B",\s*"cached_in":\s*"3\.94B",\s*"uncached_input":\s*"133M",\s*"uncached_in":\s*"133M",\s*"output":\s*"29\.3M",\s*"cache_savings":\s*"\$10,553\.41"\s*\}',
    '"totals": {"processed": "2.66B", "cached_in": "2.48B", "uncached_in": "132M", "output": "15.8M", "cache_savings": "$1,975.10"}',
    content
)

# Update models list
models_exact = [
    {"rank": 1, "model": "claude-opus-4-5", "harness": "claude_code", "harness_label": "Claude Code", "color": "#E07A5F", "cost_usd": 257.54, "cost_str": "$257.54", "share_pct": 84.8, "bar_pct": 84.8, "tokens_str": "455M", "cache_hit_pct": 95.3, "reuse_str": "20.2x"},
    {"rank": 2, "model": "gpt-5.1-cod", "harness": "openai_codex", "harness_label": "OpenAI Codex", "color": "#30D158", "cost_usd": 29.95, "cost_str": "$29.95", "share_pct": 9.9, "bar_pct": 14.5, "tokens_str": "150M", "cache_hit_pct": 96.9, "reuse_str": "31.5x"},
    {"rank": 3, "model": "claude-opus-4-0", "harness": "claude_code", "harness_label": "Claude Code", "color": "#E07A5F", "cost_usd": 7.15, "cost_str": "$7.15", "share_pct": 2.4, "bar_pct": 6.0, "tokens_str": "4.87M", "cache_hit_pct": 94.1, "reuse_str": "18.4x"},
    {"rank": 4, "model": "claude-sonnet-4-5", "harness": "claude_code", "harness_label": "Claude Code", "color": "#E07A5F", "cost_usd": 6.20, "cost_str": "$6.20", "share_pct": 2.0, "bar_pct": 5.5, "tokens_str": "22M", "cache_hit_pct": 95.0, "reuse_str": "24.8x"},
    {"rank": 5, "model": "claude-opus-4-5-high", "harness": "claude_code", "harness_label": "Claude Code", "color": "#E07A5F", "cost_usd": 1.38, "cost_str": "$1.38", "share_pct": 0.5, "bar_pct": 4.5, "tokens_str": "1.57M", "cache_hit_pct": 94.6, "reuse_str": "22.1x"},
    {"rank": 6, "model": "claude-sonnet-4-5-high", "harness": "claude_code", "harness_label": "Claude Code", "color": "#E07A5F", "cost_usd": 0.59, "cost_str": "$0.59", "share_pct": 0.2, "bar_pct": 3.5, "tokens_str": "1.35M", "cache_hit_pct": 94.8, "reuse_str": "23.4x"},
    {"rank": 7, "model": "claude-opus-4-0-tier2", "harness": "claude_code", "harness_label": "Claude Code", "color": "#E07A5F", "cost_usd": 0.25, "cost_str": "$0.25", "share_pct": 0.1, "bar_pct": 2.5, "tokens_str": "46.8K", "cache_hit_pct": 94.0, "reuse_str": "17.9x"},
    {"rank": 8, "model": "gpt-4-luna", "harness": "openai_codex", "harness_label": "OpenAI Codex", "color": "#30D158", "cost_usd": 0.14, "cost_str": "$0.14", "share_pct": 0.1, "bar_pct": 2.0, "tokens_str": "4.44M", "cache_hit_pct": 96.4, "reuse_str": "28.0x"},
    {"rank": 9, "model": "claude-opus-4-5-medium", "harness": "claude_code", "harness_label": "Claude Code", "color": "#E07A5F", "cost_usd": 0.12, "cost_str": "$0.12", "share_pct": 0.1, "bar_pct": 1.8, "tokens_str": "289K", "cache_hit_pct": 94.5, "reuse_str": "21.0x"},
    {"rank": 10, "model": "gemini-2.0-flash", "harness": "antigravity", "harness_label": "Antigravity", "color": "#2997FF", "cost_usd": 0.12, "cost_str": "$0.12", "share_pct": 0.1, "bar_pct": 1.8, "tokens_str": "385K", "cache_hit_pct": 93.8, "reuse_str": "35.2x"},
    {"rank": 11, "model": "claude-sonnet-4-5-medium", "harness": "claude_code", "harness_label": "Claude Code", "color": "#E07A5F", "cost_usd": 0.11, "cost_str": "$0.11", "share_pct": 0.1, "bar_pct": 1.6, "tokens_str": "135K", "cache_hit_pct": 94.2, "reuse_str": "22.5x"},
    {"rank": 12, "model": "claude-haiku-4-5-20251001", "harness": "claude_code", "harness_label": "Claude Code", "color": "#E07A5F", "cost_usd": 0.10, "cost_str": "$0.10", "share_pct": 0.1, "bar_pct": 1.5, "tokens_str": "77.3K", "cache_hit_pct": 92.0, "reuse_str": "14.2x"},
    {"rank": 13, "model": "claude-haiku-4-5", "harness": "claude_code", "harness_label": "Claude Code", "color": "#E07A5F", "cost_usd": 0.03, "cost_str": "$0.03", "share_pct": 0.1, "bar_pct": 1.2, "tokens_str": "615K", "cache_hit_pct": 93.1, "reuse_str": "16.4x"},
    {"rank": 14, "model": "antigravity-model-1218", "harness": "antigravity", "harness_label": "Antigravity", "color": "#2997FF", "cost_usd": 0.00, "cost_str": "Unpriced", "share_pct": 38.8, "bar_pct": 65.0, "tokens_str": "1.03B", "cache_hit_pct": 94.2, "reuse_str": "42.3x"},
    {"rank": 15, "model": "gemini-2.0-flash-x", "harness": "antigravity", "harness_label": "Antigravity", "color": "#2997FF", "cost_usd": 0.00, "cost_str": "Unpriced", "share_pct": 19.5, "bar_pct": 42.0, "tokens_str": "520M", "cache_hit_pct": 93.7, "reuse_str": "36.8x"},
    {"rank": 16, "model": "antigravity-model-1222", "harness": "antigravity", "harness_label": "Antigravity", "color": "#2997FF", "cost_usd": 0.00, "cost_str": "Unpriced", "share_pct": 7.6, "bar_pct": 22.0, "tokens_str": "202M", "cache_hit_pct": 93.5, "reuse_str": "29.6x"},
    {"rank": 17, "model": "antigravity-model-1417", "harness": "antigravity", "harness_label": "Antigravity", "color": "#2997FF", "cost_usd": 0.00, "cost_str": "Unpriced", "share_pct": 3.8, "bar_pct": 12.0, "tokens_str": "102M", "cache_hit_pct": 93.4, "reuse_str": "25.1x"}
]

models_json_str = json.dumps(models_exact)
content = re.sub(
    r'"model_breakdown":\s*\[.*?\](?=,\s*"day_breakdown")',
    f'"model_breakdown": {models_json_str}',
    content,
    flags=re.DOTALL
)

with open("aether_pulse_leaderboard.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Aether Pulse HTML updated successfully with exact T3 screenshot dataset.")
