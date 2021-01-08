#%%
import os
import asyncio
from typing import (Any, Union, Tuple)
from pyppeteer import (launch, connect)

#%%
async def run_snapshots(
    html_path: str,
    snapshot: Any,
    delay: int = 0,
    snap_fps:int = 24,
    frame_n:int = 1,
    intervals:list = [],
    browser: Any = None,
    **kwargs
) -> list:
    # You can load remote html file or local file
    if not html_path.startswith("http"):
        html_path = "file://" + os.path.abspath(html_path)

    # You can use browserless by docker(chrome browser)
    """
    $ docker pull browserless/chrome:latest
    $ docker run -d -p 3000:3000 --shm-size 2gb --name browserless --restart always \
      -e "DEBUG=browserless/chrome" -e "MAX_CONCURRENT_SESSIONS=10" \
      browserless/chrome:latest
    # the args `remoteAddress` is "ws://<server IP>:3000"
    """
    remote_address = kwargs.get("remoteAddress")
    if browser:
        _browser = browser
    elif remote_address is not None:
        _browser = await connect({
            "browserWSEndpoint": remote_address
        })
    else:
        _browser = await launch({
            "headless": kwargs.get("headless", True),
            "args": kwargs.get("args", [
                    "--start-maximized"
                ]
            )
        })


    # Init and config page
    page = await _browser.newPage()
    await page.setViewport({
        "width": 1920,
        "height": 1080
    })
    await page.setJavaScriptEnabled(enabled=True)
    await page.goto(html_path)

    # Sleep until delay
    await asyncio.sleep(delay)

    # Make snapshots
    rets = []
    # Get or set intervals
    intervals = intervals or [1/snap_fps] * frame_n
    for itvl in intervals:
        await asyncio.sleep(itvl)
        snap_data = await snapshot(page)
        rets.append(snap_data)

    # Remote session: disconnect the browser session
    # Passed browser: close page
    # Inner-opened browser: close browser
    if remote_address is not None:
        await _browser.disconnect()
    elif browser is None:
        await _browser.close()
    else:
        await page.close()

    return rets

# %%
# %%
async def query_snapshot(page, query="body"):
    eles = await page.querySelectorAll(query)
    rets = []
    for ele in eles:
        rets.append(await ele.screenshot())
    return rets

async def fullpage_snapshot(page):
    scoll_down_js = """
() => {
    var totalHeight = 0;
    var distance = 100;
    var timer = setInterval(() => {
        var scrollHeight = document.body.scrollHeight;
        window.scrollBy(0, distance);
        totalHeight += distance;
        if (totalHeight >= scrollHeight) {
            clearInterval(timer);
            resolve();
        }
    }, 100);
}
    """
    await page.evaluate(scoll_down_js)
    return await page.screenshot({
        "fullPage": True
    })


# %%
if __name__ == "__main__":
    png = asyncio.run(run_snapshots("https://baidu.com", query_snapshot))
    with open("xixi.png", "wb") as f:
        f.write(png[0])
