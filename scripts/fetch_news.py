import feedparser, json, os, requests

RSS_FEEDS = {
    "반도체·전자":    "https://news.google.com/rss/search?q=반도체&hl=ko&gl=KR&ceid=KR:ko",
    "채권·금융":      "https://news.google.com/rss/search?q=금리+연준&hl=ko&gl=KR&ceid=KR:ko",
    "자동차·배터리":  "https://news.google.com/rss/search?q=전기차+배터리&hl=ko&gl=KR&ceid=KR:ko",
    "바이오·헬스케어":"https://news.google.com/rss/search?q=바이오+임상&hl=ko&gl=KR&ceid=KR:ko",
    "환율·원자재":    "https://news.google.com/rss/search?q=달러+환율&hl=ko&gl=KR&ceid=KR:ko",
    "클라우드·인프라":"https://news.google.com/rss/search?q=데이터센터+AI&hl=ko&gl=KR&ceid=KR:ko",
}
EMOJI_MAP  = {"반도체·전자":"🔬","채권·금융":"🏛️","자동차·배터리":"🔋","바이오·헬스케어":"💊","환율·원자재":"💱","클라우드·인프라":"🖥️"}
COLOR_MAP  = {"반도체·전자":"#2563EB","채권·금융":"#059669","자동차·배터리":"#D97706","바이오·헬스케어":"#7C3AED","환율·원자재":"#C8392B","클라우드·인프라":"#0891B2"}

API_KEY = os.environ["GEMINI_API_KEY"]
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={API_KEY}"

def summarize(titles, industry):
    prompt = f"""다음은 오늘 '{industry}' 분야의 주요 뉴스 헤드라인이야.
1) 이 뉴스들을 아우르는 핵심 키워드(10자 이내)를 한 줄로 알려줘.
2) 주린이(주식 완전 초보)도 이해할 수 있는 언어로 핵심 내용을 3줄로 요약해줘.
반드시 JSON만 반환해. 예시:
{{"keyword":"AI 반도체 전쟁","summary":["문장1","문장2","문장3"]}}

헤드라인 목록:
{chr(10).join(f'- {t}' for t in titles[:10])}"""

    res = requests.post(API_URL, json={
        "contents": [{"parts": [{"text": prompt}]}]
    })
    text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
    text = text.strip().replace("```json","").replace("```","")
    return json.loads(text)

results = []
for i, (industry, url) in enumerate(RSS_FEEDS.items()):
    feed   = feedparser.parse(url)
    titles = [e.title for e in feed.entries[:15]]
    if not titles:
        continue
    data = summarize(titles, industry)
    results.append({
        "keyword":  data["keyword"],
        "industry": industry,
        "emoji":    EMOJI_MAP[industry],
        "color":    COLOR_MAP[industry],
        "featured": i == 0,
        "summary":  data["summary"]
    })

with open("data/today.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("✅ today.json 생성 완료")
