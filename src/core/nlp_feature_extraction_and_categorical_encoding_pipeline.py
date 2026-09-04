"""
NLP Feature Extraction and Categorical Encoding Pipeline Module.

Required Functions:
- Series.str.contains()
- Series.str.extract()
- Series.str.replace()
- Series.str.split()
- Series.str.lower()
- pd.get_dummies()
- pd.cut()

Logic: News headline, contains bitcoin, extract $50000 regex, replace chars, split, lower, get_dummies, cut bins Low/Mid/High.
"""

from typing import Dict
import pandas as pd


def extract_nlp_and_categorical_features(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Extracts structured entities, regex patterns, text tokens, dummy flags, and bucketed quantile bins from headlines/text.
    """
    results = {}

    # Sample dataset containing market news headlines for NLP processing
    news_df = pd.DataFrame({
        "headline_id": [1, 2, 3, 4, 5],
        "headline_text": [
            "BITCOIN surges past $65000 target level!",
            "Ethereum upgraded to PoS with $3500 gas optimization",
            "Solana ecosystem expands with $150 transaction volume",
            "Cardano price stabilizes around $0.50 range",
            "Dogecoin memes trigger $0.15 breakout move"
        ],
        "market_cap_tier": [1000000000, 300000000, 50000000, 10000000, 5000000]
    })

    # 1. Series.str.lower(): Convert headlines to lower-case
    news_df["clean_headline"] = news_df["headline_text"].str.lower()

    # 2. Series.str.contains(): Check for keyword target 'bitcoin' or 'ethereum'
    news_df["is_btc_mentioned"] = news_df["clean_headline"].str.contains("bitcoin|btc")

    # 3. Series.str.extract(): Regex extraction of target dollar values (e.g., $65000)
    news_df["extracted_target_price"] = news_df["headline_text"].str.extract(r"(\$\d+)")

    # 4. Series.str.replace(): Clean special punctuation characters
    news_df["sanitized_text"] = news_df["headline_text"].str.replace(r"[!$]", "", regex=True)

    # 5. Series.str.split(): Tokenize headline text into word lists
    news_df["headline_tokens"] = news_df["clean_headline"].str.split(" ")

    results["nlp_extracted"] = news_df

    # 6. pd.cut(): Quantile / range binning into Low, Mid, High market cap buckets
    bins = [0, 20000000, 200000000, 2000000000]
    labels = ["Low_Cap", "Mid_Cap", "High_Cap"]
    news_df["cap_category"] = pd.cut(news_df["market_cap_tier"], bins=bins, labels=labels)

    # 7. pd.get_dummies(): One-hot categorical encoding
    dummy_df = pd.get_dummies(news_df[["cap_category"]], prefix="tier", drop_first=False)
    encoded_news_df = pd.concat([news_df, dummy_df], axis=1)

    results["categorical_encoded"] = encoded_news_df

    return results
