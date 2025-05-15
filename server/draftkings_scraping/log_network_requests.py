import asyncio
from playwright.async_api import async_playwright
import sys
import os
import datetime

async def log_network_requests(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        requests = []
        responses = []

        def handle_request(request):
            requests.append({
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type,
                "headers": dict(request.headers),
            })

        async def handle_response(response):
            try:
                body = await response.body()
                content_type = response.headers.get('content-type', '')
                responses.append({
                    "url": response.url,
                    "status": response.status,
                    "content_type": content_type,
                    "body": body,
                })
            except Exception as e:
                responses.append({
                    "url": response.url,
                    "status": response.status if hasattr(response, 'status') else None,
                    "content_type": response.headers.get('content-type', '') if hasattr(response, 'headers') else '',
                    "body": None,
                    "error": str(e),
                })

        page.on("request", handle_request)
        page.on("response", lambda response: asyncio.create_task(handle_response(response)))

        try:
            print(f"Navigating to {url} ...")
            response = await page.goto(url, wait_until="networkidle", timeout=60000)
            if not response or not response.ok:
                print(f"Page load failed: {response.status if response else 'No response'}")
            else:
                print(f"Page loaded: {response.status}")
        except Exception as e:
            print(f"Error during navigation: {e}")

        await asyncio.sleep(5)  # Ensure all requests/responses are captured

        base_dir = os.path.dirname(__file__)
        log_path = os.path.join(base_dir, "network_requests.log")
        responses_dir = os.path.join(base_dir, "network_responses")
        os.makedirs(responses_dir, exist_ok=True)

        # Map url to response file for logging
        response_file_map = {}
        for i, resp in enumerate(responses, 1):
            ext = ".bin"
            if resp.get("content_type", "").startswith("application/json"):
                ext = ".json"
            elif resp.get("content_type", "").startswith("text/"):
                ext = ".txt"
            filename = f"response_{i}{ext}"
            filepath = os.path.join(responses_dir, filename)
            try:
                if resp["body"] is not None:
                    with open(filepath, "wb") as f:
                        f.write(resp["body"])
                    response_file_map[resp["url"]] = filename
                else:
                    response_file_map[resp["url"]] = None
            except Exception as e:
                response_file_map[resp["url"]] = None

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Network requests log for {url}\n")
            f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n\n")
            for i, req in enumerate(requests, 1):
                f.write(f"Request {i}:\n")
                f.write(f"  Method: {req['method']}\n")
                f.write(f"  URL: {req['url']}\n")
                f.write(f"  Resource Type: {req['resource_type']}\n")
                f.write(f"  Headers:\n")
                for k, v in req['headers'].items():
                    f.write(f"    {k}: {v}\n")
                # Reference response file if available
                resp_file = response_file_map.get(req['url'])
                if resp_file:
                    f.write(f"  Response Body File: {os.path.join('network_responses', resp_file)}\n")
                else:
                    f.write(f"  Response Body File: Not available\n")
                f.write("\n")

        print(f"\nTotal requests captured: {len(requests)}\n")
        print(f"Network request details saved to: {log_path}\n")
        print(f"Response bodies saved in: {responses_dir}\n")
        for i, req in enumerate(requests, 1):
            print(f"{i}. {req['method']} {req['url']} [{req['resource_type']}]")
        await browser.close()

if __name__ == "__main__":
    url = "https://sportsbook.draftkings.com/event/dal-cowboys-%40-phi-eagles/32225662"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    asyncio.run(log_network_requests(url)) 