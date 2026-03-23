import random
import asyncio
import random
import os
import time
import math
from urllib.parse import urlparse
from typing import Optional, Dict, Any, List, Union, Literal, Callable

from playwright.async_api import async_playwright, Page as AsyncPage, ElementHandle

class PlaywrightAPI:
    def __init__(self, ws_endpoint: str):
        """
        Args:
            ws_endpoint: Remote debugging websocket URL or address (e.g. 127.0.0.1:9222)
        """
        self.remote_debug = ws_endpoint
        self.browser = None
        self.context = None
        self.page = None
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.quit_all()
        
    async def connect(self):
        try:
            self.playwright = await async_playwright().start()
            # Thêm http:// nếu không có
            debug_url = self.remote_debug
            if not debug_url.startswith(('http://', 'https://')):
                debug_url = f"http://{debug_url}"
                
            self.browser = await self.playwright.chromium.connect_over_cdp(
                debug_url,
                timeout=30000
            )
            
            # Lấy context hiện có
            contexts = self.browser.contexts
            if contexts:
                self.context = contexts[0]  # Lấy context đầu tiên
            
            # Nếu không có context hoặc page nào, tạo mới
            if not self.context:
                self.context = await self.browser.new_context()
            
            # Lấy page hiện tại hoặc tạo mới nếu cần
            pages = self.context.pages
            if pages:
                self.page = pages[0]
            else:
                self.page = await self.context.new_page()
                
            await self.add_browser_fingerprint_evasions()
            
            return self.page
                
        except Exception as e:
            await self.quit_all()
            raise e
    
    """Dưới đây là 3 hàm dùng để chạy cùng lúc nhiều auto, không phải để chuyển tab"""
    async def new_page(self) -> AsyncPage:
        """Create and return a new page in the current browser context"""
        self.page = await self.context.new_page()
        return self.page
    
    async def get_page_default(self) -> AsyncPage:
        """Get the default page in the current browser context"""
        return self.page

    async def get_all_pages(self) -> List[AsyncPage]:
        """Get all open pages"""
        return self.context.pages

    async def switch_page(self, page_index: int):
        """
        Switch to and focus on a specific page by index
        Args:
            page_index: Index of the page to switch to (0-based)
        """
        pages = await self.get_all_pages()
        if 0 <= page_index < len(pages):
            self.page = pages[page_index]
            await self.page.bring_to_front()
        else:
            raise ValueError(f"Invalid page index: {page_index}. Available pages: 0-{len(pages)-1}")

    # Navigation
    async def sleep(self, seconds: int):
        await asyncio.sleep(seconds)
        
    async def open_url(self, url: str, page: Optional[AsyncPage] = None, timeout: int = 40000, wait_until: Literal['commit', 'domcontentloaded', 'load', 'networkidle'] = "load"):
        target_page: AsyncPage = page if page else self.page            
        await target_page.goto(url, wait_until=wait_until, timeout=timeout)
        
    async def reload(self, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.reload()
        
    async def get_current_url(self, page: Optional[AsyncPage] = None) -> str:
        """
        Lấy URL trang hiện tại
        """
        target_page: AsyncPage = page if page else self.page
        return target_page.url
        
    async def go_back(self, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.go_back()
        
    async def close_tab(self, tab_index: int = None, url: str = None):
        """
        Close specified tab based on index or URL
        Args:
            tab_index: Index of tab to close
            url: URL pattern to match for closing tab
        """
        try:
            pages = await self.get_all_pages()
            
            # Trường hợp đóng tab dựa trên URL
            if url:
                # Tìm tất cả các tab có URL match với pattern
                matching_pages = [page for page in pages if url in page.url]
                
                if not matching_pages:
                    raise ValueError(f"No tab found with URL containing: {url}")
                
                for target_page in matching_pages:
                    # Nếu đang đóng tab hiện tại
                    if target_page == self.page:
                        await target_page.close()
                        # Chuyển sang tab đầu tiên còn lại nếu có
                        remaining_pages = await self.get_all_pages()
                        if remaining_pages:
                            self.page = remaining_pages[0]
                    else:
                        await target_page.close()
                return

            # Trường hợp không chỉ định index (đóng tab hiện tại)
            if tab_index is None:
                await self.page.close()
                # Chuyển sang tab đầu tiên còn lại nếu có
                remaining_pages = await self.get_all_pages()
                if remaining_pages:
                    self.page = remaining_pages[0]
                return

            # Trường hợp đóng tab theo index
            if 0 <= tab_index < len(pages):
                target_page = pages[tab_index]
                
                # Nếu đang đóng tab hiện tại
                if target_page == self.page:
                    await target_page.close()
                    remaining_pages = await self.get_all_pages()
                    if remaining_pages:
                        self.page = remaining_pages[0]
                else:
                    await target_page.close()
            else:
                raise ValueError(f"Invalid tab index: {tab_index}. Available tabs: 0-{len(pages)-1}")
            
        except Exception as e:
            raise Exception(f"Error closing tab: {str(e)}")

    async def quit_all(self):
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    # Interaction
    async def click(self, selector: str, page: Optional[AsyncPage] = None, button: Literal['left', 'middle', 'right'] = 'left', click_count: int = 1, delay: float = 0.5, timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        await target_page.click(selector, delay=delay, button=button, click_count=click_count, timeout=timeout)

    
    async def human_click(self, selector: str, page: Optional[AsyncPage] = None, 
                     randomize_position: bool = True, click_delay: Optional[float] = None,
                     mouse_tracking: bool = True, timeout: int = 5000):
        """
        Thực hiện click như người dùng thực với nhiều hành vi tự nhiên
        
        Args:
            selector: CSS selector của phần tử cần click
            page: Trang để thực hiện hành vi, mặc định là self.page
            randomize_position: Có nên click vào vị trí ngẫu nhiên trong phần tử hay không
            click_delay: Thời gian giữ chuột trước khi nhả (giây)
            mouse_tracking: Di chuyển chuột theo đường cong trước khi click
            timeout: Thời gian chờ tối đa (ms)
        """
        target_page = page if page else self.page
        
        # Đợi phần tử xuất hiện trên trang
        element = await target_page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise ValueError(f"Element not found: {selector}")
        
        # Đảm bảo phần tử nhìn thấy được trên màn hình
        await element.scroll_into_view_if_needed()
        
        # Đôi khi tạm dừng một khoảng thời gian ngắn trước khi thao tác
        # (như người dùng đang "suy nghĩ")
        if random.random() < 0.4:  # 40% xác suất tạm dừng
            await asyncio.sleep(random.uniform(0.2, 0.8))
        
        # Lấy kích thước và vị trí của phần tử
        box = await element.bounding_box()
        if not box:
            raise ValueError("Không thể xác định vị trí phần tử")
        
        # Xác định điểm click - có thể click chính giữa hoặc tại vị trí ngẫu nhiên
        if randomize_position:
            # Click vào vị trí ngẫu nhiên trong phần tử (không quá sát mép)
            x = box['x'] + box['width'] * random.uniform(0.2, 0.8)
            y = box['y'] + box['height'] * random.uniform(0.2, 0.8)
        else:
            # Click vào chính giữa phần tử
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
        
        # Di chuyển chuột theo đường cong đến phần tử trước khi click
        if mouse_tracking:
            await self.perform_human_like_mouse_movements(target_page, num_points=random.randint(2, 5))
            
            # Di chuyển chuột đến phần tử theo đường cong Bezier
            current_pos = await target_page.evaluate("""
                () => ({
                    x: window.mouseX || window.innerWidth/2, 
                    y: window.mouseY || window.innerHeight/2
                })
            """)
            
            # Điểm kiểm soát đường cong
            ctrl_x = (current_pos['x'] + x) / 2 + random.uniform(-40, 40)
            ctrl_y = (current_pos['y'] + y) / 2 + random.uniform(-30, 30)
            
            steps = random.randint(8, 15)
            for i in range(1, steps + 1):
                t = i / steps
                # Công thức đường cong bậc 2
                pos_x = (1-t)**2 * current_pos['x'] + 2*(1-t)*t*ctrl_x + t**2*x
                pos_y = (1-t)**2 * current_pos['y'] + 2*(1-t)*t*ctrl_y + t**2*y
                
                # Thêm độ run nhẹ
                if random.random() < 0.3:
                    pos_x += random.uniform(-2, 2)
                    pos_y += random.uniform(-2, 2)
                    
                await target_page.mouse.move(pos_x, pos_y)
                await asyncio.sleep(random.uniform(0.01, 0.03))
        else:
            # Di chuyển trực tiếp đến vị trí click
            await target_page.mouse.move(x, y)
        
        # Hover trước khi click
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Thời gian giữ chuột (giây)
        click_delay = click_delay or random.uniform(0.05, 0.15)
        
        # Thực hiện click
        await target_page.mouse.down()
        await asyncio.sleep(click_delay)
        await target_page.mouse.up()
        
        # Đôi khi thêm hành động sau khi click (như di chuyển chuột đi)
        if random.random() < 0.3:  # 30% xác suất
            await asyncio.sleep(random.uniform(0.2, 0.5))
            # Di chuyển chuột đi một chút sau khi click
            await target_page.mouse.move(
                x + random.uniform(-50, 50),
                y + random.uniform(-30, 30)
            )
        
    async def dblclick(self, selector: str, page: Optional[AsyncPage] = None, delay: float = 0.5, timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        await target_page.dblclick(selector, force=True, delay=delay, timeout=timeout)
        
    async def hover(self, selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        await target_page.hover(selector, timeout=timeout)
 
        
    async def human_hover(self, selector: str, page: Optional[AsyncPage] = None, 
                     duration_range: tuple = (0.5, 2.5), jitter: bool = True, 
                     perform_tracking: bool = True, timeout: int = 5000):
        """
        Hover giống người dùng thực với các đặc điểm tự nhiên
        
        Args:
            selector: CSS selector của phần tử cần hover
            page: Trang để thực hiện hover, mặc định là self.page
            duration_range: Khoảng thời gian hover (min, max) tính bằng giây
            jitter: Có tạo chuyển động lăng xăng nhẹ trong khi hover không
            perform_tracking: Có tạo đường đi chuột đến phần tử không
            timeout: Thời gian chờ tối đa (ms)
        """
        target_page = page if page else self.page
        
        # Tìm phần tử
        element = await target_page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise ValueError(f"Element not found: {selector}")
        
        # Cuộn đến phần tử
        await element.scroll_into_view_if_needed()
        
        # Tạm dừng một chút trước khi di chuyển đến phần tử
        if random.random() < 0.3:
            await asyncio.sleep(random.uniform(0.2, 0.7))
        
        # Lấy kích thước và vị trí phần tử
        box = await element.bounding_box()
        if not box:
            raise ValueError("Không thể xác định vị trí phần tử")
        
        # Xác định điểm hover (mặc định hơi lệch khỏi trung tâm)
        hover_x = box['x'] + box['width'] * random.uniform(0.3, 0.7)
        hover_y = box['y'] + box['height'] * random.uniform(0.3, 0.7)
        
        # Di chuyển chuột đến phần tử theo đường cong tự nhiên
        if perform_tracking:
            # Lấy vị trí hiện tại của chuột
            current_pos = await target_page.evaluate("""
                () => ({ 
                    x: window.mouseX || window.innerWidth/2, 
                    y: window.mouseY || window.innerHeight/2 
                })
            """)
            
            # Tạo đường cong
            ctrl_x = (current_pos['x'] + hover_x) / 2 + random.uniform(-50, 50)
            ctrl_y = (current_pos['y'] + hover_y) / 2 + random.uniform(-40, 40)
            
            # Di chuyển theo đường cong
            steps = random.randint(10, 20)
            for i in range(1, steps + 1):
                t = i / steps
                
                # Độ trễ khác nhau khi tiếp cận phần tử
                if i > steps * 0.8:  # Gần đến đích
                    await asyncio.sleep(random.uniform(0.02, 0.04))  # Chậm lại
                else:
                    await asyncio.sleep(random.uniform(0.01, 0.02))
                    
                # Công thức đường cong bậc 2
                pos_x = (1-t)**2 * current_pos['x'] + 2*(1-t)*t*ctrl_x + t**2*hover_x
                pos_y = (1-t)**2 * current_pos['y'] + 2*(1-t)*t*ctrl_y + t**2*hover_y
                
                # Thêm độ run nhẹ
                if random.random() < 0.3:
                    pos_x += random.uniform(-2, 2)
                    pos_y += random.uniform(-2, 2)
                    
                await target_page.mouse.move(pos_x, pos_y)
        else:
            # Di chuyển trực tiếp đến phần tử
            await target_page.mouse.move(hover_x, hover_y)
        
        # Thời gian hover
        hover_duration = random.uniform(*duration_range)
        hover_start = time.time()
        
        # Mô phỏng chuột "lăng xăng" nhẹ trong khi hover
        if jitter:
            while time.time() - hover_start < hover_duration:
                # Di chuyển trong phạm vi nhỏ xung quanh điểm hover
                jitter_x = hover_x + random.uniform(-5, 5)
                jitter_y = hover_y + random.uniform(-5, 5)
                
                # Đảm bảo vẫn trong phạm vi phần tử
                jitter_x = max(box['x'] + 2, min(box['x'] + box['width'] - 2, jitter_x))
                jitter_y = max(box['y'] + 2, min(box['y'] + box['height'] - 2, jitter_y))
                
                await target_page.mouse.move(jitter_x, jitter_y)
                await asyncio.sleep(random.uniform(0.1, 0.3))
        else:
            # Hover tĩnh
            await asyncio.sleep(hover_duration)
        
        # Xác suất di chuyển chuột ra khỏi phần tử sau khi hover
        if random.random() < 0.7:  # 70% xác suất
            # Di chuyển chuột ra khỏi phần tử sau khi hover
            move_x = hover_x + random.uniform(-100, 100)
            move_y = hover_y + random.uniform(-50, 50)
            
            # Đảm bảo trong viewport
            viewport = await target_page.evaluate("() => { return {width: window.innerWidth, height: window.innerHeight} }")
            move_x = max(10, min(viewport['width'] - 10, move_x))
            move_y = max(10, min(viewport['height'] - 10, move_y))
            
            # Di chuyển với tốc độ ngẫu nhiên
            await target_page.mouse.move(move_x, move_y)
    
    async def click_and_hold(self, selector: str, delay: float = 1.0, page: Optional[AsyncPage] = None, timeout: int = 5000):
        """
        Click và giữ element trong n giây
        Args:
            selector: Selector của element
            delay: Thời gian giữ (giây)
            page: Optional specific page
        """
        target_page: AsyncPage = page if page else self.page
        
        # Di chuyển chuột đến element
        element = await target_page.query_selector(selector)
        if not element:
            raise Exception(f"Element not found: {selector}")
            
        # Lấy vị trí giữa element
        box = await element.bounding_box()
        x = box['x'] + box['width'] / 2
        y = box['y'] + box['height'] / 2
        
        # Click và giữ
        await target_page.mouse.move(x, y)
        await target_page.mouse.down()
        await self.sleep(delay)
        await target_page.mouse.up()

    async def touch_element(
        self,
        selector: str,
        page: Optional[AsyncPage] = None,
        is_tap_random: bool = False,
        num_position_tap: int = 1,
        tap_count: int = 100,
        time_limit: int | None = None,
        delay: float = 1,
        timeout: int = 5000
    ):
        """Nếu tap_count được truyền, hàm sẽ đếm số lần chạm và dừng khi đạt số lượng tap_count.
        Nếu chỉ có time_limit (ms), hàm sẽ chạm liên tục với khoảng cách giữa các lần chạm là 0 - 300ms cho đến khi hết thời gian time_limit.
        Nếu cả hai đều được truyền, hàm sẽ dừng khi đạt một trong hai điều kiện (đủ số lần chạm hoặc hết thời gian).
        Num position tap ý chỉ số vị trí chạm, mặc định là 1
        """
        try:
            target_page: AsyncPage = page if page else self.page
            script = f"""
            function eventTouch(element, isTapRandom, numPositionTap, tapCount, timeLimit) {{
            function createTouch(element, x, y) {{
                return new Touch({{
                    identifier: Date.now(),
                    target: element,
                    clientX: x,
                    clientY: y,
                    pageX: x + window.scrollX,
                    pageY: y + window.scrollY,
                    screenX: x + window.screenX,
                    screenY: y + window.screenY,
                }});
            }}

            function triggerTouch(element, x, y) {{
                const touch = createTouch(element, x, y);

                const touchEventStart = new TouchEvent("touchstart", {{
                    bubbles: true,
                    cancelable: true,
                    touches: [touch],
                    targetTouches: [touch],
                    changedTouches: [touch],
                }});

                element.dispatchEvent(touchEventStart);

                const touchEventEnd = new TouchEvent("touchend", {{
                    bubbles: true,
                    cancelable: true,
                    touches: [],
                    targetTouches: [],
                    changedTouches: [touch],
                }});

                element.dispatchEvent(touchEventEnd);
            }}

            function getRandomPosition(element) {{
                const rect = element.getBoundingClientRect();
                let x = rect.left + rect.width / 2;
                let y = rect.top + rect.height / 2;
                if (isTapRandom) {{
                    x = rect.left + Math.random() * rect.width;
                    y = rect.top + Math.random() * rect.height;
                }}
                return {{ x, y }};
            }}

            function tap(element, numPositionTap, tapCount, timeLimit ) {{
                const startTime = Date.now();
                let taps = 0;

                function performTap() {{
                    if (tapCount && taps >= tapCount) {{
                        return;
                    }}

                    if (timeLimit && (Date.now() - startTime) >= timeLimit) {{
                        return;
                    }}

                    // Perform taps with random positions
                    for (let i = 0; i < numPositionTap; i++) {{
                        const {{ x, y }} = getRandomPosition(element);
                        triggerTouch(element, x, y);  // Trigger touch at a new random position each time
                    }}

                    taps += 1;

                    // Random delay between 0 and 300ms
                    const randomDelay = Math.floor(Math.random() * 300);

                    setTimeout(performTap, randomDelay);
                }}

                performTap();
            }}

            if (element) {{
                tap(element, numPositionTap, tapCount, timeLimit );
            }}
            }}
        
            eventTouch({element}, {is_tap_random}, {num_position_tap}, {tap_count}, {time_limit});
            """
            if time_limit is not None:
                time_limit = time_limit * 1000
            # Tìm phần tử để thực hiện chạm
            element = await self.wait_for_selector(selector, page=target_page, timeout=timeout)
            await self.run_js(script, page=target_page)
            await self.sleep(delay)
            
        except Exception as e:
            raise Exception(f"Không tìm thấy element {selector} để touch. Error: {e}")
        
    async def human_type(self, selector: str, text: str, page: Optional[AsyncPage] = None, 
              human_like: bool = True, delay: float = 0.3, timeout: int = 5000, 
              typing_pattern: str = "normal"):
        """
        Type text into an element with advanced human-like behavior
        
        Args:
            selector: Element selector
            text: Text to type
            page: Target page
            human_like: Whether to simulate human-like typing patterns
            delay: Fixed delay between keystrokes (if human_like is False)
            timeout: Maximum wait time for element
            typing_pattern: Typing pattern style ("normal", "fast", "careful", "distracted")
        """
        target_page: AsyncPage = page if page else self.page
        
        # Đợi element xuất hiện và focus vào nó
        element = await target_page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise ValueError(f"Element not found: {selector}")
        
        # Di chuyển chuột đến element trước khi focus (đôi khi)
        if random.random() < 0.7:
            box = await element.bounding_box()
            if box:
                click_x = box['x'] + box['width'] * random.uniform(0.2, 0.8)
                click_y = box['y'] + box['height'] * random.uniform(0.2, 0.8)
                await target_page.mouse.move(click_x, click_y)
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await target_page.mouse.click(click_x, click_y)
        else:
            await element.focus()
        
        # Xóa nội dung hiện có (nếu có)
        if random.random() < 0.6:  # 60% trường hợp xóa nội dung trước khi gõ
            current_value = await target_page.evaluate(f"""
                (selector) => {{
                    const el = document.querySelector(selector);
                    return el ? el.value : '';
                }}
            """, selector)
            
            if current_value:
                if len(current_value) > 10 or random.random() < 0.7:
                    # Chọn tất cả văn bản và xóa
                    await target_page.keyboard.press('Control+A')
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    await target_page.keyboard.press('Delete')
                else:
                    # Xóa từng ký tự
                    for _ in range(len(current_value)):
                        await target_page.keyboard.press('Backspace')
                        await asyncio.sleep(random.uniform(0.03, 0.08))
        
        if human_like:
            # Thiết lập thông số dựa trên kiểu gõ
            if typing_pattern == "fast":
                # Người gõ nhanh, có kinh nghiệm
                base_delay = 0.03
                delay_variation = 0.04
                burst_prob = 0.4
                typo_prob = 0.02
                think_prob = 0.05
            elif typing_pattern == "careful":
                # Người gõ cẩn thận, chậm
                base_delay = 0.1
                delay_variation = 0.1
                burst_prob = 0.05
                typo_prob = 0.01
                think_prob = 0.2
            elif typing_pattern == "distracted":
                # Người gõ không tập trung, nhiều lỗi
                base_delay = 0.08
                delay_variation = 0.15
                burst_prob = 0.2
                typo_prob = 0.08
                think_prob = 0.15
            else:  # "normal"
                # Người gõ bình thường
                base_delay = 0.07
                delay_variation = 0.08
                burst_prob = 0.2
                typo_prob = 0.04
                think_prob = 0.1
            
            # Phân tích văn bản để hiểu cấu trúc
            is_password = await target_page.evaluate(f"""
                (selector) => {{
                    const el = document.querySelector(selector);
                    return el && (el.type === 'password' || 
                            el.getAttribute('type') === 'password' || 
                            el.getAttribute('autocomplete') === 'current-password');
                }}
            """, selector)
            
            # Phân tích từ và cụm từ (để gõ nhanh hơn trong một từ)
            words = text.split(' ')
            for word_idx, word in enumerate(words):
                # Mô phỏng đang "nghĩ" giữa các từ
                if word_idx > 0 and random.random() < think_prob:
                    await asyncio.sleep(random.uniform(0.3, 1.2))
                
                # Đôi khi gõ từ nhanh theo cụm
                is_burst_mode = random.random() < burst_prob and len(word) > 3
                
                for i, char in enumerate(word):
                    # Xử lý trường hợp gõ sai và sửa lại (không áp dụng cho password)
                    if not is_password and random.random() < typo_prob and char.isalnum():
                        # Gõ một ký tự sai
                        wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz') if char.isalpha() else random.choice('0123456789')
                        await target_page.keyboard.type(wrong_char)
                        
                        # Ngừng một chút để "nhận ra lỗi"
                        await asyncio.sleep(random.uniform(0.1, 0.4))
                        
                        # Sửa lỗi (đôi khi nhấn backspace nhiều lần do nhấn nhầm)
                        if random.random() < 0.2:  # 20% nhấn backspace nhiều lần
                            for _ in range(random.randint(2, 3)):
                                await target_page.keyboard.press('Backspace')
                                await asyncio.sleep(random.uniform(0.08, 0.15))
                            for _ in range(random.randint(0, 1)):  # Đôi khi gõ lại ký tự đã xóa trước đó
                                await target_page.keyboard.press('Backspace')
                                await asyncio.sleep(random.uniform(0.05, 0.1))
                        else:
                            await target_page.keyboard.press('Backspace')
                            await asyncio.sleep(random.uniform(0.08, 0.2))
                    
                    # Gõ ký tự đúng
                    await target_page.keyboard.type(char)
                    
                    # Tính toán độ trễ cho ký tự tiếp theo
                    if is_password:
                        # Gõ mật khẩu thường nhanh và đều hơn
                        typing_delay = base_delay + random.uniform(0, delay_variation)
                    else:
                        # Tạo độ trễ khác nhau dựa trên vị trí và loại ký tự
                        
                        # Delay ngắn hơn cho ký tự trong burst mode
                        if is_burst_mode:
                            typing_delay = base_delay * 0.6 + random.uniform(0, delay_variation * 0.5)
                        else:
                            # Gõ chậm hơn cho các ký tự đặc biệt
                            if char in '!@#$%^&*()_+-=[]{}|;:\'",.<>?/\\':
                                typing_delay = base_delay * 1.5 + random.uniform(0, delay_variation * 1.2)
                            # Gõ chậm hơn cho chữ hoa (vì phải nhấn Shift)
                            elif char.isupper():
                                typing_delay = base_delay * 1.3 + random.uniform(0, delay_variation)
                            # Gõ chậm hơn cho số
                            elif char.isdigit():
                                typing_delay = base_delay * 1.2 + random.uniform(0, delay_variation)
                            # Gõ nhanh hơn cho chữ thường
                            else:
                                typing_delay = base_delay + random.uniform(0, delay_variation)
                            
                            # Gõ chậm hơn ở đầu và cuối từ
                            if i == 0 or i == len(word) - 1:
                                typing_delay *= 1.2
                    
                    await asyncio.sleep(typing_delay)
                
                # Thêm khoảng trắng sau mỗi từ (trừ từ cuối cùng)
                if word_idx < len(words) - 1:
                    await target_page.keyboard.type(' ')
                    await asyncio.sleep(random.uniform(0.08, 0.2))
                    
            # Đôi khi di chuyển chuột sau khi gõ
            if random.random() < 0.3 and not is_password:  # Ít khi làm việc này với mật khẩu
                await self.perform_human_like_mouse_movements(target_page, num_points=2)
        else:
            # Gõ bình thường với delay cố định nếu không cần human-like
            await target_page.type(selector, text, delay=delay or 0)
            
    async def keyboards_press_multi(self, sequence: List[str], delay: float = 100):
        """
        Mô phỏng một chuỗi các phím được nhấn
        Args:
            sequence: List các phím cần nhấn (VD: ['Control', 'a', 'Delete'])
            delay: Độ trễ giữa các lần nhấn phím (milliseconds)
        """
        for key in sequence:
            await self.keyboard_press(key)
            await self.sleep(delay / 1000)
        
    async def type(self, selector: str, value: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        """Ghi giá trị ngay lập tức vào một element"""
        target_page: AsyncPage = page if page else self.page
        await target_page.fill(selector, value, timeout=timeout)
        
    async def press(self, selector: str, key: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        await target_page.press(selector, key, timeout=timeout)
        
    async def check(self, selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        await target_page.check(selector, timeout=timeout)
        
    async def uncheck(self, selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        await target_page.uncheck(selector, timeout=timeout)
        
    async def select_option(self, selector: str, value: Union[str, List[str]], page: Optional[AsyncPage] = None, timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        await target_page.select_option(selector, value, timeout=timeout)
        
    async def scroll_to_element(self, selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        """
        Scroll đến element
        Args:
            selector: Selector của element
            page: Optional specific page
        """
        target_page: AsyncPage = page if page else self.page
        element = await target_page.query_selector(selector)
        if element:
            await element.scroll_into_view_if_needed()
            
    async def scroll_by_amount(self, x: int = 0, y: int = 0, page: Optional[AsyncPage] = None, 
                            human_like: bool = True):
        """
        Scroll theo khoảng cách x, y với chuyển động tự nhiên
        """
        target_page: AsyncPage = page if page else self.page
        
        if not human_like:
            await target_page.evaluate(f"window.scrollBy({x}, {y})")
            return
        
        # Scroll với hành vi người dùng thực
        total_distance_x, total_distance_y = x, y
        steps = random.randint(5, 15) if abs(y) > 200 or abs(x) > 200 else random.randint(3, 8)
        
        # Thêm đôi khi "quá đà" rồi điều chỉnh lại (rất người dùng)
        overshoot = random.random() < 0.3
        
        if overshoot:
            # Quá khoảng cách một chút
            overshoot_x = x * random.uniform(1.1, 1.2) if x != 0 else 0
            overshoot_y = y * random.uniform(1.1, 1.2) if y != 0 else 0
        else:
            overshoot_x, overshoot_y = x, y
        
        # Tạo đường cong easing
        for i in range(steps):
            t = i / (steps - 1)
            
            # Easing function (ease-out)
            power = 3
            progress = 1 - pow(1 - t, power)
            
            # Tính khoảng cách cho bước này
            step_x = overshoot_x * (progress - (previous_progress if i > 0 else 0))
            step_y = overshoot_y * (progress - (previous_progress if i > 0 else 0))
            previous_progress = progress
            
            # Thêm jitter nhỏ
            if i > 0 and i < steps - 1:
                step_x += random.uniform(-2, 2)
                step_y += random.uniform(-2, 2)
            
            # Thực hiện scroll
            await target_page.evaluate(f"window.scrollBy({step_x}, {step_y})")
            await asyncio.sleep(random.uniform(0.01, 0.03))
        
        # Nếu quá đà, điều chỉnh lại
        if overshoot:
            await asyncio.sleep(random.uniform(0.2, 0.4))
            correction_x = x - overshoot_x
            correction_y = y - overshoot_y
            
            await target_page.evaluate(f"window.scrollBy({correction_x}, {correction_y})")
        
    async def human_scroll(self, direction: str = 'down', distance: Optional[int] = None,
                      page: Optional[AsyncPage] = None, smooth: bool = True, speed: str = 'normal'):
        """
        Thực hiện cuộn trang giống hành vi người dùng thực.
        
        Args:
            direction: Hướng cuộn ('up', 'down', 'left', 'right')
            distance: Khoảng cách cuộn (pixel). Nếu None, sẽ chọn ngẫu nhiên
            page: Trang để thực hiện, mặc định là self.page
            smooth: Có cuộn mượt hay không
            speed: Tốc độ cuộn ('slow', 'normal', 'fast')
        """
        target_page = page if page else self.page
        
        # Xác định kích thước viewport và scroll hiện tại
        metrics = await target_page.evaluate("""
            () => {
                return {
                    scrollHeight: document.documentElement.scrollHeight,
                    clientHeight: document.documentElement.clientHeight,
                    scrollWidth: document.documentElement.scrollWidth,
                    clientWidth: document.documentElement.clientWidth,
                    scrollTop: document.documentElement.scrollTop,
                    scrollLeft: document.documentElement.scrollLeft
                };
            }
        """)
        
        # Nếu không chỉ định distance, tự động tính toán khoảng cách phù hợp
        if distance is None:
            if direction == 'down':
                distance = random.randint(300, min(800, metrics['scrollHeight'] - metrics['scrollTop'] - metrics['clientHeight']))
            elif direction == 'up':
                distance = random.randint(300, min(800, metrics['scrollTop']))
            elif direction == 'right':
                distance = random.randint(100, min(400, metrics['scrollWidth'] - metrics['scrollLeft'] - metrics['clientWidth']))
            elif direction == 'left':
                distance = random.randint(100, min(400, metrics['scrollLeft']))
        
        # Đảm bảo distance không âm
        distance = max(0, distance)
        
        # Thiết lập tốc độ cuộn dựa trên thông số
        if speed == 'slow':
            duration = random.uniform(1.5, 2.5)
            steps = random.randint(20, 30)
        elif speed == 'fast':
            duration = random.uniform(0.3, 0.8)
            steps = random.randint(8, 15)
        else:  # 'normal'
            duration = random.uniform(0.8, 1.5)
            steps = random.randint(15, 25)
        
        # Xác định vector cuộn
        dx = 0
        dy = 0
        if direction == 'down':
            dy = distance
        elif direction == 'up':
            dy = -distance
        elif direction == 'right':
            dx = distance
        elif direction == 'left':
            dx = -distance
        
        start_time = time.time()
        
        # Lưu giữ tổng khoảng cách đã cuộn
        total_scrolled_x = 0
        total_scrolled_y = 0
        
        if smooth:
            # Tạo đường cong easing cho cuộn mượt mà
            for i in range(steps):
                # Tỷ lệ hoàn thành
                progress = i / (steps - 1)
                
                # Áp dụng hàm easing (ease-in-out quad)
                if progress < 0.5:
                    t = 2 * progress * progress
                else:
                    t = -1 + (4 - 2 * progress) * progress
                
                # Tính khoảng cách cần cuộn cho bước này
                current_x = dx * t
                current_y = dy * t
                
                # Khoảng cách cho bước này
                step_x = int(current_x - total_scrolled_x)
                step_y = int(current_y - total_scrolled_y)
                
                # Thêm nhiễu nhẹ để giống cuộn tự nhiên hơn (trừ bước đầu tiên và cuối cùng)
                if 0 < i < steps - 1:
                    jitter_x = random.uniform(-2, 2) if dx != 0 else 0
                    jitter_y = random.uniform(-2, 2) if dy != 0 else 0
                    step_x += jitter_x
                    step_y += jitter_y
                
                # Thực hiện cuộn
                await target_page.evaluate(f"window.scrollBy({step_x}, {step_y})")
                
                # Cập nhật tổng khoảng cách đã cuộn
                total_scrolled_x += step_x
                total_scrolled_y += step_y
                
                # Tính thời gian trễ để đảm bảo tổng thời gian đúng
                elapsed = time.time() - start_time
                target_elapsed = duration * progress
                delay = max(0, target_elapsed - elapsed)
                
                # Đôi khi tạm dừng giữa chừng để đọc nội dung (chỉ khi cuộn dọc)
                if direction in ['up', 'down'] and i > steps // 2 and random.random() < 0.15:
                    await asyncio.sleep(random.uniform(0.2, 0.8))
                else:
                    await asyncio.sleep(delay)
        else:
            # Cuộn nhanh không mượt (ít bước hơn)
            quick_steps = random.randint(3, 6)
            for i in range(quick_steps):
                step_x = int(dx / quick_steps)
                step_y = int(dy / quick_steps)
                
                # Thêm độ không đồng đều
                if i != quick_steps - 1:  # Không áp dụng cho bước cuối
                    step_x = int(step_x * random.uniform(0.8, 1.2))
                    step_y = int(step_y * random.uniform(0.8, 1.2))
                
                # Thực hiện cuộn
                await target_page.evaluate(f"window.scrollBy({step_x}, {step_y})")
                
                # Cộng dồn khoảng cách đã cuộn
                total_scrolled_x += step_x
                total_scrolled_y += step_y
                
                # Độ trễ ngắn giữa các bước
                await asyncio.sleep(random.uniform(0.05, 0.15))
        
        # Đôi khi scroll quá đà rồi điều chỉnh lại (chỉ khi cuộn mượt)
        if smooth and random.random() < 0.3:
            overshoot_ratio = random.uniform(0.05, 0.15)
            overshoot_x = int(dx * overshoot_ratio) if dx != 0 else 0
            overshoot_y = int(dy * overshoot_ratio) if dy != 0 else 0
            
            # Cuộn quá đà một chút
            await target_page.evaluate(f"window.scrollBy({overshoot_x}, {overshoot_y})")
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            # Cuộn lại
            await target_page.evaluate(f"window.scrollBy({-overshoot_x}, {-overshoot_y})")
        
        # Đôi khi thực hiện các hành vi sau khi cuộn như di chuyển chuột
        if random.random() < 0.4:
            await self.perform_human_like_mouse_movements(target_page, num_points=random.randint(1, 3))
        
        # Đôi khi dừng lại để đọc sau khi cuộn xong (chỉ khi cuộn dọc)
        if direction in ['up', 'down'] and random.random() < 0.3:
            await asyncio.sleep(random.uniform(0.5, 2.0))   
        
    # State
    async def wait_for_selector(self, selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000, state: str = "visible"):
        target_page: AsyncPage = page if page else self.page
        return await target_page.wait_for_selector(selector, state=state, timeout=timeout)
    
    async def wait_for_load_state(self, page: Optional[AsyncPage] = None, state: Literal['domcontentloaded', 'load', 'networkidle'] = "load", timeout: int = 5000):
        try:
            target_page: AsyncPage = page if page else self.page
            options = {}
            if timeout:
                options['timeout'] = timeout
                
            await target_page.wait_for_load_state(state, **options)
            
        except Exception as e:
            raise Exception(f"Timeout waiting for page load state '{state}': {str(e)}")
        
    # Content
    async def get_text(self, selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000) -> str:
        target_page: AsyncPage = page if page else self.page
        return await target_page.text_content(selector, timeout=timeout)
    
    async def get_attribute(self, selector: str, name: str, page: Optional[AsyncPage] = None, timeout: int = 5000) -> Optional[str]:
        target_page: AsyncPage = page if page else self.page
        return await target_page.get_attribute(selector, name, timeout=timeout)
    
    async def get_inner_html(self, selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000) -> str:
        target_page: AsyncPage = page if page else self.page
        return await target_page.inner_html(selector, timeout=timeout)

    # DOM
    async def element_exists(self, selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000) -> bool:
        """Kiểm tra xem phần tử có tồn tại hay không với thời gian chờ."""
        try:
            target_page: AsyncPage = page if page else self.page
            await self.wait_for_selector(selector, page=target_page, timeout=timeout)
            return True
        except:
            return False

    async def count_elements(self, selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000) -> int:
        try:
            target_page: AsyncPage = page if page else self.page
            try:
                await self.wait_for_selector(selector, page=target_page, timeout=timeout)
            except Exception:
                return 0
                    
            elements = await target_page.query_selector_all(selector)
            return len(elements)
        
        except Exception as e:
            raise Exception(f"Error counting elements with selector '{selector}': {str(e)}")
        
    async def download_image_from_element(self, selector: str, save_path: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        """
        Tải ảnh từ src của element
        Args:
            selector: Selector của element chứa ảnh
            save_path: Đường dẫn lưu ảnh
            page: Optional specific page
        """
        target_page: AsyncPage = page if page else self.page
        
        # Lấy src của ảnh
        element = await target_page.query_selector(selector)
        if not element:
            raise Exception(f"Image element not found: {selector}")
            
        src = await element.get_attribute('src')
        if not src:
            raise Exception(f"No src attribute found for element: {selector}")
        
        # Tải ảnh
        response = await target_page.request.get(src)
        image_data = await response.body()
        
        # Lưu ảnh
        with open(save_path, 'wb') as f:
            f.write(image_data)

    async def wait_for_event(self, event: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        """
        Wait for a specific event to occur
        Args:
            event: Event name to wait for
            timeout: Maximum time to wait
        """
        target_page: AsyncPage = page if page else self.page
        await target_page.wait_for_event(event, timeout=timeout)
    
    async def run_js(self, expression: str, page: Optional[AsyncPage] = None) -> Any:
        # Hàm này chỉ chạy js bình thường nếu có kết quả thì trả kết quả về như chuỗi, số hay dữ liệu gì đó
        target_page: AsyncPage = page if page else self.page
        return await target_page.evaluate(expression)
    
    async def run_js_2(self, expression: str, page: Optional[AsyncPage] = None) -> Any:
        # Hàm này trả về element và có thể thực hiện thao tác trên element đó luôn
        # Ví dụ 2: Lấy DOM element 
        # element_handle = await api.run_js_2('document.querySelector("button.submit")')  
        # Trả về JSHandle tham chiếu đến button element

        # Bạn có thể tiếp tục tương tác với JSHandle:
        # await element_handle.click(force=True)
        
        target_page: AsyncPage = page if page else self.page
        return await target_page.evaluate_handle(expression)
    
    async def setup_clipboard_monitor(self, page: Optional[AsyncPage] = None):
        """
        Thiết lập hook để theo dõi clipboard trên trang web
        
        Args:
            page: Optional specific page
        
        Returns:
            None
        """
        target_page: AsyncPage = page if page else self.page
        
        # Thiết lập hook để theo dõi clipboard
        await target_page.evaluate("""
            window.lastCopiedText = '';
            
            // Lưu navigator.clipboard.writeText gốc
            if (!window._originalClipboardWriteText) {
                window._originalClipboardWriteText = navigator.clipboard.writeText;
            }
            
            // Override navigator.clipboard.writeText
            navigator.clipboard.writeText = function(text) {
                window.lastCopiedText = text;
                console.log('Text copied to clipboard:', text);
                return window._originalClipboardWriteText(text);
            };
        """)
        
    async def copy_to_clipboard(self, text: str = None, page: Optional[AsyncPage] = None):
        """
        Copy nội dung vào clipboard hoặc lấy nội dung từ clipboard
        
        Args:
            text: Nội dung cần copy vào clipboard (None nếu chỉ muốn lấy nội dung hiện tại)
            page: Optional specific page
        
        Returns:
            Văn bản trong clipboard
        """
        target_page: AsyncPage = page if page else self.page
        
        # Đảm bảo hook đã được thiết lập
        await self.setup_clipboard_monitor(page=target_page)
        
        # Nếu có text được truyền vào, thực hiện copy ngay
        if text:
            await target_page.evaluate(f"""
                navigator.clipboard.writeText("{text.replace('"', '\\"')}");
            """)
        
        # Đọc giá trị hiện tại trong clipboard
        copied_text = await target_page.evaluate("window.lastCopiedText")
        
        return copied_text 
        
    async def connect_to_iframe_by_xpath(self, selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000) -> Optional[AsyncPage]:
        """Switch context to an iframe"""
        try:
            # Đợi iframe xuất hiện
            target_page: AsyncPage = page if page else self.page
            await self.wait_for_selector(selector, page=target_page, timeout=timeout)
            
            # Lấy frame object
            return await target_page.frame_locator(selector).frame_locator("iframe").first
        except Exception as e:
            raise Exception(f"Failed to switch to iframe: {str(e)}")
    
    async def connect_to_iframe_by_name(self, name: str, page: Optional[AsyncPage] = None) -> Optional[AsyncPage]:
        """Lấy frame theo tên"""
        target_page: AsyncPage = page if page else self.page
        return await target_page.frame(name)
    
    async def connect_to_extension(self, id: str) -> Optional[AsyncPage]:
        """Switch context to an extension"""
        try:
            pages = await self.get_all_pages()
            for page in pages:
                if f"chrome-extension://{id}" in page.url:
                    await page.bring_to_front()
                    return page
            return None
        except Exception as e:
            raise Exception(f"Failed to switch to extension: {str(e)}")
    
    async def get_all_iframes(self, page: Optional[AsyncPage] = None) -> List:
        """Lấy danh sách tất cả frames trong trang"""
        target_page: AsyncPage = page if page else self.page
        return target_page.frames
    
    async def connect_to_main_frame(self, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        return target_page.main_frame

    # File handling
    async def upload_file(self, selector: str, file_path: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        await target_page.set_input_files(selector, file_path, timeout=timeout)

    # Screenshots
    async def screenshot(self, path: str = None, page: Optional[AsyncPage] = None, full_page: bool = False):
        target_page: AsyncPage = page if page else self.page
        return await target_page.screenshot(path=path, full_page=full_page)
    
    async def screenshot_element(self, selector: str, path: str, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        element = await target_page.query_selector(selector)
        await element.screenshot(path=path)

    # Cookies
    async def add_cookies(self, cookies: List[Dict]):
        await self.context.add_cookies(cookies)
        
    async def delete_cookie(self, name: str, domain: str = None):
        """Delete a specific cookie by name and optionally domain"""
        cookies = await self.get_cookies()
        filtered_cookies = [c for c in cookies if c['name'] != name or (domain and c['domain'] != domain)]
        await self.context.clear_cookies()
        await self.context.add_cookies(filtered_cookies)
    
    async def clear_cookies(self):
        await self.context.clear_cookies()
    
    async def get_cookies(self, key: str = None, page: Optional[AsyncPage] = None) -> List[Dict]:
        """Get cookies from current page. If key is specified, return only cookies matching that key."""
        target_page: AsyncPage = page if page else self.page
        # Lấy URL của trang hiện tại
        current_url = await target_page.url

        # Parse domain từ URL hiện tại
        current_domain = urlparse(current_url).netloc

        # Lấy tất cả cookies từ context
        all_cookies = await self.context.cookies()

        # Lọc cookies chỉ của domain hiện tại
        current_page_cookies = [
            cookie for cookie in all_cookies 
            if current_domain in cookie.get('domain', '')
        ]

        # Nếu có key được chỉ định, lọc theo key
        if key:
            return [
                cookie for cookie in current_page_cookies 
                if cookie.get('name') == key
            ]

        # Nếu không có key, trả về tất cả cookies của trang hiện tại
        return current_page_cookies
            
    # Advanced Navigation
    async def wait_for_load_page_done(self, url: str = None, page: Optional[AsyncPage] = None, wait_until: str = "load", timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        return await target_page.wait_for_navigation(url=url, wait_until=wait_until, timeout=timeout)
    
    async def wait_for_request(self, url: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        return await target_page.wait_for_request(url, timeout=timeout)
    
    async def get_request_header(self, url: str, header_key: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        """Chờ một request có URL chỉ định và lấy giá trị của header chỉ định."""
        target_page: AsyncPage = page if page else self.page
        request = await target_page.wait_for_request(url, timeout=timeout)
        return await request.headers.get(header_key, None)
    
    async def wait_for_response(self, url: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        return await target_page.wait_for_response(url, timeout=timeout).text()

    # Advanced Interaction
    async def drag_and_drop(self, source: str, target: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        await target_page.drag_and_drop(source, target, timeout=timeout)
    
    async def drag_and_drop_by_coordinates(self, source_selector: str, x: int, y: int, page: Optional[AsyncPage] = None):
        """Drag element to specific coordinates"""
        target_page: AsyncPage = page if page else self.page
        source = await target_page.query_selector(source_selector)
        await source.drag_to(x=x, y=y)
    
    async def focus(self, selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        await target_page.focus(selector, timeout=timeout)
    
    async def tap(self, selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        target_page: AsyncPage = page if page else self.page
        await target_page.tap(selector, timeout=timeout)

    # Keyboard and Mouse
    async def keyboard_down(self, key: str, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.keyboard.down(key)
    
    async def keyboard_up(self, key: str, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.keyboard.up(key)
    
    async def keyboard_press(self, key: str, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.keyboard.press(key)
    
    async def keyboard_type(self, text: str, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.keyboard.type(text)
    
    async def mouse_move(self, x: int, y: int, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.mouse.move(x, y)
    
    async def mouse_down(self, button: Literal['left', 'middle', 'right'] = "left", page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.mouse.down(button=button)
    
    async def mouse_up(self, button: Literal['left', 'middle', 'right'] = "left", page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.mouse.up(button=button)
    
    async def mouse_click(self, x: int, y: int, button: Literal['left', 'middle', 'right'] = "left", page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.mouse.click(x, y, button=button)

    # Network Interception
    async def set_request_interception(self, enabled: bool, page: Optional[AsyncPage] = None):
        """Enable or disable request interception for network modifications"""
        target_page: AsyncPage = page if page else self.page
        await target_page.set_request_interception(enabled)
    
    async def add_request_handler(self, url_pattern: str, handler: Callable):
        """Add a custom handler for intercepted network requests matching the pattern"""
        await self.route(url_pattern, handler)
    
    async def set_request_blocking(self, patterns: Union[str, List[str]], page: Optional[AsyncPage] = None):
        """
        Block network requests matching the specified URL pattern(s)
        Args:
            patterns: Single URL string or list of URL patterns to block
            page: Optional specific page to apply blocking, defaults to current page
        """
        target_page: AsyncPage = page if page else self.page
        
        async def block_handler(route):
            await route.abort()
        
        # Convert single string pattern to list
        if isinstance(patterns, str):
            patterns = [patterns]
            
        # Apply blocking for each pattern
        for pattern in patterns:
            await target_page.route(pattern, block_handler)

    async def mock_api_response(self, url_pattern: str, response_data: Dict):
        """Mock API responses matching URL pattern"""
        async def handle_route(route):
            await route.fulfill(json=response_data)
        await self.route(url_pattern, handle_route)
    
    async def unroute(self, url: str, handler: Optional[Callable] = None, page: Optional[AsyncPage] = None):
        """Dùng để bỏ tất cả thao tác đã cài với 1 request nào đó ví dụ chặn hay làm giả response, Nếu không truyền handler, nó sẽ bỏ tất cả route liên quan đến url."""
        target_page: AsyncPage = page if page else self.page
        await target_page.unroute(url, handler)
    
    async def set_offline_mode(self, offline: bool):
        """Dùng để chuyển trạng thái offline/online cho trình duyệt"""
        await self.context.set_offline(offline)
    
    async def set_geolocation(self, latitude: float, longitude: float):
        """Dùng để thay đổi vị trí địa lý của trình duyệt"""
        await self.context.set_geolocation({"latitude": latitude, "longitude": longitude})
    
    async def set_permissions(self, permissions: List[str]):
        """Dùng để cấp quyền truy cập vào các tính năng như camera, microphone, vị trí GPS, v.v."""
        await self.context.grant_permissions(permissions)

    # Storage
    async def local_storage_get_item(self, key: str, page: Optional[AsyncPage] = None) -> Optional[str]:
        target_page: AsyncPage = page if page else self.page
        return await target_page.evaluate(f'window.localStorage.getItem("{key}")')
    
    async def local_storage_set_item(self, key: str, value: str, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.evaluate(f'window.localStorage.setItem("{key}", "{value}")')
    
    async def local_storage_remove_item(self, key: str, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.evaluate(f'window.localStorage.removeItem("{key}")')
    
    async def local_storage_clear(self, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.evaluate('window.localStorage.clear()')
    
    async def session_storage_get_item(self, key: str, page: Optional[AsyncPage] = None) -> Optional[str]:
        target_page: AsyncPage = page if page else self.page
        return await target_page.evaluate(f'window.sessionStorage.getItem("{key}")')
    
    async def session_storage_set_item(self, key: str, value: str, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.evaluate(f'window.sessionStorage.setItem("{key}", "{value}")')

    # Video Recording
    async def start_video_recording(self, path: str, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.video.start(path=path)
    
    async def stop_video_recording(self, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.video.stop()

    # WebSocket
    async def wait_for_websocket(self, url: str, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        return await target_page.wait_for_websocket(url)
    
    async def on_websocket(self, callback: Callable, page: Optional[AsyncPage] = None):
        target_page: AsyncPage = page if page else self.page
        await target_page.on("websocket", callback)
        
    # Form Handling
    async def handle_single_file_upload(self, folder_path: str, file_name: str, page: Optional[AsyncPage] = None):
        """
        Xử lý upload một file duy nhất khi file chooser xuất hiện
        Args:
            folder_path: Đường dẫn đến thư mục chứa file
            file_name: Tên file cần upload
            page: Optional specific page to handle file chooser
        """
        target_page: AsyncPage = page if page else self.page
        
        file_path = os.path.join(folder_path, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        async def file_chooser_handler(file_chooser):
            await file_chooser.set_files(file_path)
            
        await target_page.on("filechooser", file_chooser_handler)
        
    async def handle_multiple_files_upload(self, folder_path: str, file_names: List[str], page: Optional[AsyncPage] = None):
        """
        Xử lý upload nhiều file khi file chooser xuất hiện
        Args:
            folder_path: Đường dẫn đến thư mục chứa các file
            file_names: List tên các file cần upload
            page: Optional specific page to handle file chooser
        """
        target_page: AsyncPage = page if page else self.page
        
        # Tạo list đường dẫn đầy đủ cho các file
        file_paths = []
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            file_paths.append(file_path)
        
        async def file_chooser_handler(file_chooser):
            await file_chooser.set_files(file_paths)
            
        await target_page.on("filechooser", file_chooser_handler)

    # Resource Optimization
    async def enable_request_compression(self):
        """Enable compression for network requests"""
        async def compress_request(route):
            request = route.request
            if request.resource_type in ['document', 'script', 'stylesheet']:
                headers = request.headers
                headers['Accept-Encoding'] = 'gzip, deflate, br'
                await route.continue_(headers=headers)
            else:
                await route.continue_()
        await self.route("**/*", compress_request)
        
    async def get_shadow_element(self, host_selector: str, shadow_selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000) -> ElementHandle:
        """
        Lấy phần tử trong Shadow DOM
        Args:
            host_selector: Selector của host element chứa shadow root
            shadow_selector: Selector của element trong shadow DOM
        Returns:
            ElementHandle của phần tử trong shadow DOM
        """
        target_page: AsyncPage = page if page else self.page
        
        # Cách tiếp cận mới: sử dụng cú pháp shadow selector của Playwright
        # Format: hostSelector >> shadowSelector
        combined_selector = f"{host_selector} >> {shadow_selector}"
        
        try:
            # Chờ element xuất hiện với timeout mặc định
            element = await target_page.wait_for_selector(combined_selector, timeout=timeout)
            return element
        except Exception as e:
            raise Exception(f"Shadow DOM element not found: {combined_selector}. Error: {str(e)}")

    async def click_shadow_element(self, host_selector: str, shadow_selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        """Click vào phần tử trong Shadow DOM"""
        target_page: AsyncPage = page if page else self.page
        combined_selector = f"{host_selector} >> {shadow_selector}"
        
        try:
            await target_page.click(combined_selector, timeout=timeout)
        except Exception as e:
            raise Exception(f"Failed to click shadow element: {combined_selector}. Error: {str(e)}")

    async def fill_shadow_element(self, host_selector: str, shadow_selector: str, value: str, page: Optional[AsyncPage] = None, timeout: int = 5000):
        """Điền giá trị vào input trong Shadow DOM"""
        target_page: AsyncPage = page if page else self.page
        combined_selector = f"{host_selector} >> {shadow_selector}"
        
        try:
            await target_page.fill(combined_selector, value, timeout=timeout)
        except Exception as e:
            raise Exception(f"Failed to fill shadow element: {combined_selector}. Error: {str(e)}")

    async def get_shadow_text(self, host_selector: str, shadow_selector: str, page: Optional[AsyncPage] = None, timeout: int = 5000) -> str:
        """Lấy text của phần tử trong Shadow DOM"""
        target_page: AsyncPage = page if page else self.page
        combined_selector = f"{host_selector} >> {shadow_selector}"
        
        try:
            return await target_page.text_content(combined_selector, timeout=timeout)
        except Exception as e:
            raise Exception(f"Failed to get text from shadow element: {combined_selector}. Error: {str(e)}")

    async def wait_for_shadow_element(self, host_selector: str, shadow_selector: str, 
                                    state: str = "visible", timeout: int = 5000, page: Optional[AsyncPage] = None):
        """
        Đợi phần tử trong Shadow DOM xuất hiện/ẩn đi
        Args:
            host_selector: Selector của host element
            shadow_selector: Selector của element trong shadow DOM
            state: 'visible', 'hidden', 'attached', 'detached'
            timeout: Thời gian đợi tối đa (ms)
            page: Optional specific page
        """
        target_page: AsyncPage = page if page else self.page
        combined_selector = f"{host_selector} >> {shadow_selector}"
        
        options = {"state": state}
        if timeout:
            options["timeout"] = timeout
            
        try:
            await target_page.wait_for_selector(combined_selector, **options)
        except Exception as e:
            raise Exception(f"Timeout waiting for shadow element: {combined_selector} with state '{state}'. Error: {str(e)}")

    async def get_shadow_attribute(self, host_selector: str, shadow_selector: str, attribute: str, page: Optional[AsyncPage] = None, timeout: int = 5000) -> str:
        """
        Lấy giá trị thuộc tính của phần tử trong Shadow DOM
        Args:
            host_selector: Selector của host element
            shadow_selector: Selector của element trong shadow DOM
            attribute: Tên thuộc tính cần lấy
            page: Optional specific page
        Returns:
            Giá trị của thuộc tính
        """
        target_page: AsyncPage = page if page else self.page
        combined_selector = f"{host_selector} >> {shadow_selector}"
        
        try:
            return await target_page.get_attribute(combined_selector, attribute, timeout=timeout)
        except Exception as e:
            raise Exception(f"Failed to get attribute '{attribute}' from shadow element: {combined_selector}. Error: {str(e)}")
    
    # Advanced Navigation
    async def wait_for_url_change(self, current_url: str, page: Optional[AsyncPage] = None, timeout: int = 30000):
        """Wait for URL to change from current value"""
        target_page: AsyncPage = page if page else self.page
        await target_page.wait_for_function(
            f'window.location.href !== "{current_url}"',
            timeout=timeout
        )

    # Dynamic Content Handling
    async def wait_for_text_content(self, selector: str, text: str, page: Optional[AsyncPage] = None, timeout: int = 30000):
        """Wait for element to contain specific text"""
        target_page: AsyncPage = page if page else self.page
        await target_page.wait_for_function(
            f'document.querySelector("{selector}").textContent.includes("{text}")',
            timeout=timeout
        )
        
    async def simulate_human_behavior(self, page: Optional[AsyncPage] = None):
        """Mô phỏng các hành vi người dùng thực trong quá trình tự động hóa"""
        target_page = page if page else self.page
        
        # 1. Thêm độ trễ ngẫu nhiên giữa các hành động
        await asyncio.sleep(random.uniform(1.2, 3.5))
        
        # 2. Di chuyển chuột không mục đích (browsing)
        await self.perform_human_like_mouse_movements(target_page)
        
        # 3. Đôi khi cuộn trang một cách tự nhiên
        if random.random() < 0.7:
            # Cuộn xuống với tốc độ thay đổi
            for _ in range(random.randint(3, 8)):
                scroll_y = random.randint(100, 300)
                await target_page.evaluate(f"window.scrollBy(0, {scroll_y})")
                await asyncio.sleep(random.uniform(0.3, 0.7))
            
            # Đôi khi cuộn lại lên
            if random.random() < 0.4:
                await asyncio.sleep(random.uniform(0.8, 2.0))
                for _ in range(random.randint(1, 4)):
                    scroll_y = random.randint(50, 200)
                    await target_page.evaluate(f"window.scrollBy(0, -{scroll_y})")
                    await asyncio.sleep(random.uniform(0.3, 0.7))
        
        # 4. Thỉnh thoảng focus vào các phần tử khác nhau
        elements = ["a", "button", "div", "p", "h2", "img"]
        for _ in range(random.randint(1, 3)):
            element = random.choice(elements)
            try:
                elements_on_page = await target_page.query_selector_all(element)
                if elements_on_page and len(elements_on_page) > 0:
                    random_element = elements_on_page[random.randint(0, min(len(elements_on_page)-1, 10))]
                    await random_element.hover()
                    await asyncio.sleep(random.uniform(0.3, 1.2))
            except:
                pass
             
    async def simulate_reading_behavior(self, page: Optional[AsyncPage] = None, min_read_time: int = 10, max_read_time: int = 40):
        """
        Mô phỏng hành vi đọc nội dung của người dùng thực.
        
        Args:
            page: Trang để thực hiện hành vi, mặc định là self.page
            min_read_time: Thời gian đọc tối thiểu (giây)
            max_read_time: Thời gian đọc tối đa (giây)
        """
        target_page = page if page else self.page
        
        # Lấy chiều cao trang
        total_height = await target_page.evaluate("document.body.scrollHeight")
        viewport_height = await target_page.evaluate("window.innerHeight")
        
        # Thời gian đọc tổng cộng (giây)
        total_read_time = random.uniform(min_read_time, max_read_time)
        start_time = time.time()
        
        # Vị trí cuộn hiện tại
        current_position = 0
        
        while time.time() - start_time < total_read_time:
            # Mô phỏng đọc từng đoạn
            await asyncio.sleep(random.uniform(1.5, 4.0))  # Thời gian dừng đọc
            
            # Xác định đoạn văn bản chính để focus vào đọc
            try:
                paragraphs = await target_page.query_selector_all('p, h1, h2, h3, h4, article, section')
                if paragraphs and len(paragraphs) > 0:
                    # Chọn ngẫu nhiên một đoạn văn để focus
                    random_para = paragraphs[min(int(current_position/viewport_height * len(paragraphs)), len(paragraphs)-1)]
                    
                    # Cuộn đến đoạn văn đó
                    await random_para.scroll_into_view_if_needed()
                    
                    # Di chuyển chuột đến đoạn văn
                    await random_para.hover()
                    
                    # Mô phỏng đọc bằng cách select một phần văn bản (thỉnh thoảng)
                    if random.random() < 0.2:
                        # Chọn một phần văn bản
                        await target_page.evaluate("""
                            (element) => {
                                const range = document.createRange();
                                const selection = window.getSelection();
                                range.selectNodeContents(element);
                                selection.removeAllRanges();
                                selection.addRange(range);
                                
                                // Chọn chỉ một phần của đoạn văn
                                const textLength = element.textContent.length;
                                if (textLength > 10) {
                                    const start = Math.floor(Math.random() * (textLength - 10));
                                    const end = start + Math.floor(Math.random() * 10) + 3;
                                    
                                    if (document.createRange && window.getSelection) {
                                        range.setStart(element.firstChild, start);
                                        range.setEnd(element.firstChild, end);
                                        selection.removeAllRanges();
                                        selection.addRange(range);
                                    }
                                }
                            }
                        """, random_para)
                        
                        # Giữ lựa chọn một lúc
                        await asyncio.sleep(random.uniform(0.5, 1.2))
                        
                        # Bỏ lựa chọn
                        if random.random() < 0.5:
                            await target_page.evaluate("""
                                () => {
                                    window.getSelection().removeAllRanges();
                                }
                            """)
                
                # Cuộn xuống với tốc độ đọc tự nhiên
                scroll_step = random.randint(100, 300)
                current_position = min(current_position + scroll_step, total_height - viewport_height)
                await target_page.evaluate(f"window.scrollTo(0, {current_position})")
                
                # Thỉnh thoảng cuộn lên một chút, như khi đọc lại nội dung
                if random.random() < 0.15 and current_position > viewport_height:
                    scroll_back = random.randint(100, 300)
                    current_position = max(0, current_position - scroll_back)
                    await target_page.evaluate(f"window.scrollTo(0, {current_position})")
                    await asyncio.sleep(random.uniform(1.0, 2.5))
                    
            except Exception as e:
                # Xử lý lỗi nếu có
                pass
                
            # Mô phỏng chuyển động mắt bằng cách di chuyển chuột một chút
            try:
                x_offset = random.randint(-10, 10)
                y_offset = random.randint(-5, 20)
                
                # Lấy vị trí chuột hiện tại
                mouse_pos = await target_page.evaluate("""
                    () => {
                        return {
                            x: window.mouseX || window.innerWidth/2,
                            y: window.mouseY || window.innerHeight/3
                        }
                    }
                """)
                
                # Di chuyển chuột một chút như đang đọc
                x = mouse_pos['x'] + x_offset
                y = mouse_pos['y'] + y_offset
                await target_page.mouse.move(x, y)
                
            except Exception as e:
                pass         
             
    async def simulate_search_behavior(self, search_selector: str, search_terms: List[str], page: Optional[AsyncPage] = None):
        """
        Mô phỏng hành vi tìm kiếm tự nhiên.
        
        Args:
            search_selector: CSS selector của ô tìm kiếm
            search_terms: Danh sách các từ khóa tìm kiếm
            page: Trang để thực hiện hành vi, mặc định là self.page
        """
        target_page = page if page else self.page
        
        if not search_terms:
            return
        
        search_term = random.choice(search_terms)
        
        # Đôi khi thực hiện một số thao tác trước khi tìm kiếm
        if random.random() < 0.3:
            await self.perform_human_like_mouse_movements(target_page)
        
        # Focus vào ô tìm kiếm
        try:
            await target_page.focus(search_selector)
            await asyncio.sleep(random.uniform(0.3, 0.8))
            
            # Xóa nội dung ô tìm kiếm (nếu có)
            await target_page.evaluate(f"""
                (selector) => {{
                    const input = document.querySelector(selector);
                    if (input) input.value = '';
                }}
            """, search_selector)
            
            # Nhập từ khóa tìm kiếm kiểu người dùng thực
            for i, char in enumerate(search_term):
                # Tạo độ trễ không đều giữa các ký tự
                if i > 0:
                    # Tạo độ trễ dài hơn ở giữa các từ
                    if search_term[i-1] == ' ':
                        await asyncio.sleep(random.uniform(0.3, 0.7))
                    else:
                        typing_speed = random.normalvariate(0.1, 0.05)  # Mean: 100ms, StdDev: 50ms
                        await asyncio.sleep(max(0.05, min(0.3, typing_speed)))
                
                # Đôi khi mắc lỗi và sửa
                if random.random() < 0.05 and char.isalpha():  # 5% cơ hội gõ sai
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    await target_page.type(search_selector, wrong_char, delay=0)
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    await target_page.keyboard.press('Backspace')
                    await asyncio.sleep(random.uniform(0.1, 0.2))
                
                # Gõ ký tự thực
                await target_page.type(search_selector, char, delay=0)
            
            # Đôi khi dừng lại và suy nghĩ trước khi nhấn Enter
            if random.random() < 0.4:
                await asyncio.sleep(random.uniform(0.8, 2.0))
                
                # Đôi khi sửa lại từ khóa tìm kiếm
                if random.random() < 0.3:
                    backspaces = random.randint(1, min(3, len(search_term)))
                    for _ in range(backspaces):
                        await target_page.keyboard.press('Backspace')
                        await asyncio.sleep(random.uniform(0.1, 0.3))
                    
                    # Thêm vài ký tự mới
                    additional_text = " " + random.choice(["best", "review", "how to", "vs", "price"])
                    for char in additional_text:
                        await target_page.type(search_selector, char, delay=0)
                        await asyncio.sleep(random.uniform(0.1, 0.2))
            
            # Nhấn Enter để tìm kiếm
            await asyncio.sleep(random.uniform(0.3, 0.7))
            await target_page.keyboard.press('Enter')
            
            # Đợi kết quả tìm kiếm
            await target_page.wait_for_load_state('networkidle')
            
            # Mô phỏng xem các kết quả tìm kiếm
            if random.random() < 0.8:  # 80% cơ hội xem qua kết quả
                await self.simulate_reading_behavior(target_page, 
                                                min_read_time=5, 
                                                max_read_time=15)
                
        except Exception as e:
            # Xử lý lỗi nếu có
            pass         
             
    async def simulate_browsing_items(self, item_selector: str, page: Optional[AsyncPage] = None, 
                                min_items: int = 3, max_items: int = 8):
        """
        Mô phỏng hành vi duyệt qua các mục (sản phẩm, bài viết, v.v.)
        
        Args:
            item_selector: CSS selector chọn các mục (sản phẩm, bài viết)
            page: Trang để thực hiện hành vi, mặc định là self.page
            min_items: Số mục tối thiểu để xem
            max_items: Số mục tối đa để xem
        """
        target_page = page if page else self.page
        
        try:
            # Lấy danh sách các mục
            items = await target_page.query_selector_all(item_selector)
            if not items:
                return
            
            # Quyết định số lượng mục cần xem
            num_items = min(random.randint(min_items, max_items), len(items))
            
            # Bắt đầu từ vị trí ngẫu nhiên nếu có nhiều mục
            start_index = 0
            if len(items) > num_items:
                start_index = random.randint(0, len(items) - num_items)
            
            # Duyệt qua từng mục
            for i in range(start_index, start_index + num_items):
                if i >= len(items):
                    break
                    
                # Cuộn đến mục này
                await items[i].scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
                # Di chuyển chuột đến mục
                try:
                    box = await items[i].bounding_box()
                    if box:
                        # Di chuyển chuột đến vị trí ngẫu nhiên trong mục
                        x = box['x'] + random.uniform(box['width'] * 0.2, box['width'] * 0.8)
                        y = box['y'] + random.uniform(box['height'] * 0.2, box['height'] * 0.8)
                        
                        # Di chuyển chuột với quỹ đạo tự nhiên
                        current_position = await target_page.evaluate("""
                            () => {
                                return {
                                    x: window.mouseX || window.innerWidth/2,
                                    y: window.mouseY || window.innerHeight/2
                                }
                            }
                        """)
                        
                        # Tạo đường cong cho di chuyển chuột
                        steps = random.randint(10, 20)
                        for step in range(1, steps + 1):
                            progress = step / steps
                            ease = -4 * progress * progress + 4 * progress  # easing function
                            
                            # Thêm đường cong vào quỹ đạo
                            curve_x = math.sin(progress * math.pi) * random.uniform(5, 20)
                            curve_y = math.cos(progress * math.pi * 0.5) * random.uniform(5, 15)
                            
                            # Tính toán vị trí mới
                            next_x = current_position['x'] + (x - current_position['x']) * ease + curve_x
                            next_y = current_position['y'] + (y - current_position['y']) * ease + curve_y
                            
                            await target_page.mouse.move(next_x, next_y)
                            await asyncio.sleep(random.uniform(0.01, 0.03))
                        
                        # Hover trên mục
                        await asyncio.sleep(random.uniform(0.5, 2.0))
                        
                        # Đôi khi thực hiện các thao tác với mục
                        if random.random() < 0.3:  # 30% cơ hội click vào mục
                            # Click vào mục
                            await target_page.mouse.click(x, y)
                            
                            # Đợi trang mới tải
                            await target_page.wait_for_load_state('networkidle')
                            
                            # Đọc nội dung
                            await self.simulate_reading_behavior(target_page, 
                                                            min_read_time=8, 
                                                            max_read_time=30)
                            
                            # Quay lại trang trước
                            await target_page.go_back()
                            await target_page.wait_for_load_state('networkidle')
                            
                            # Cập nhật lại danh sách mục vì DOM có thể đã thay đổi
                            items = await target_page.query_selector_all(item_selector)
                except Exception as e:
                    # Bỏ qua lỗi và tiếp tục với mục tiếp theo
                    continue
                    
                # Đôi khi scroll chậm để đọc mục hiện tại
                if random.random() < 0.4:
                    await asyncio.sleep(random.uniform(1.0, 3.0))
        
        except Exception as e:
            # Xử lý lỗi nếu có
            pass       
             
    async def simulate_form_filling(self, form_data: Dict[str, str], page: Optional[AsyncPage] = None, submit_selector: str = "button[type='submit']"):
        """
        Mô phỏng hành vi điền form giống người dùng thực.
        
        Args:
            form_data: Dictionary với key là CSS selector và value là giá trị cần điền
            page: Trang để thực hiện hành vi, mặc định là self.page
            submit_selector: CSS selector của nút submit form
        """
        target_page = page if page else self.page
        
        try:
            # Thứ tự điền form ngẫu nhiên (nhưng thường là từ trên xuống)
            selectors = list(form_data.keys())
            if random.random() < 0.8:  # 80% trường hợp điền theo thứ tự
                random.shuffle(selectors)  # Shuffle nhẹ nhàng
            
            # Điền từng trường
            for selector in selectors:
                # Đôi khi di chuyển chuột một cách tự nhiên trước khi focus
                if random.random() < 0.7:
                    await self.perform_human_like_mouse_movements(target_page, num_points=random.randint(1, 3))
                
                # Scroll đến phần tử nếu cần
                try:
                    element = await target_page.query_selector(selector)
                    if element:
                        await element.scroll_into_view_if_needed()
                        
                        # Đôi khi nhấp chuột vào trường trước khi nhập
                        if random.random() < 0.8:
                            await element.click(delay=random.uniform(30, 100))
                        else:
                            await element.focus()
                        
                        # Đợi một chút trước khi bắt đầu gõ
                        await asyncio.sleep(random.uniform(0.3, 1.0))
                        
                        # Nếu là trường password, điền nhanh hơn và ít lỗi hơn
                        is_password = await target_page.evaluate(f"""
                            (selector) => {{
                                const el = document.querySelector(selector);
                                return el && (el.type === 'password' || el.getAttribute('autocomplete') === 'current-password');
                            }}
                        """, selector)
                        
                        value = form_data[selector]
                        
                        # Kiểm tra xem đây có phải là dropdown không
                        is_dropdown = await target_page.evaluate(f"""
                            (selector) => {{
                                const el = document.querySelector(selector);
                                return el && (el.tagName === 'SELECT');
                            }}
                        """, selector)
                        
                        if is_dropdown:
                            # Xử lý dropdown - chọn option
                            await target_page.select_option(selector, value)
                            await asyncio.sleep(random.uniform(0.5, 1.0))
                        else:
                            # Xử lý input thông thường
                            
                            # Xóa nội dung hiện có
                            current_value = await target_page.evaluate(f"""
                                (selector) => {{
                                    const el = document.querySelector(selector);
                                    return el ? el.value : '';
                                }}
                            """, selector)
                            
                            if current_value:
                                # Xóa nội dung hiện có
                                if len(current_value) > 15 or random.random() < 0.3:
                                    # Select all và xóa
                                    await target_page.keyboard.down('Control')  # hoặc Meta trên macOS
                                    await target_page.keyboard.press('a')
                                    await target_page.keyboard.up('Control')
                                    await asyncio.sleep(random.uniform(0.2, 0.4))
                                    await target_page.keyboard.press('Backspace')
                                else:
                                    # Xóa từng ký tự
                                    for _ in range(len(current_value)):
                                        await target_page.keyboard.press('Backspace')
                                        await asyncio.sleep(random.uniform(0.05, 0.1))
                            
                            # Nhập văn bản mới
                            for i, char in enumerate(value):
                                # Điều chỉnh tốc độ gõ
                                if is_password:
                                    # Gõ nhanh hơn với mật khẩu
                                    typing_speed = random.uniform(0.05, 0.15)
                                else:
                                    # Tốc độ không đều cho các ký tự bình thường
                                    base_speed = random.normalvariate(0.1, 0.05)
                                    
                                    # Chậm hơn sau dấu câu hoặc khoảng trắng
                                    if i > 0 and value[i-1] in ['.', ',', ' ', '-']:
                                        typing_speed = base_speed + random.uniform(0.1, 0.3)
                                    else:
                                        typing_speed = max(0.05, min(0.3, base_speed))
                                    
                                    # Đôi khi dừng lại để "suy nghĩ"
                                    if random.random() < 0.05:
                                        typing_speed += random.uniform(0.3, 0.8)
                                
                                # Đôi khi gõ sai và sửa lại (chỉ áp dụng cho text, không phải password)
                                if not is_password and random.random() < 0.03 and char.isalnum():
                                    typo_char = random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
                                    await target_page.type(selector, typo_char, delay=0)
                                    await asyncio.sleep(random.uniform(0.1, 0.3))
                                    await target_page.keyboard.press('Backspace')
                                    await asyncio.sleep(random.uniform(0.1, 0.2))
                                
                                # Gõ ký tự chính xác
                                await target_page.type(selector, char, delay=0)
                                await asyncio.sleep(typing_speed)
                        
                        # Đợi một chút sau khi điền xong trường này
                        await asyncio.sleep(random.uniform(0.3, 1.2))
                
                except Exception as e:
                    # Bỏ qua lỗi và tiếp tục với trường tiếp theo
                    continue
            
            # Đôi khi di chuyển chuột một chút trước khi submit
            if random.random() < 0.5:
                await self.perform_human_like_mouse_movements(target_page, num_points=random.randint(1, 3))
            
            # Submit form
            submit_button = await target_page.query_selector(submit_selector)
            if submit_button:
                # Scroll đến nút submit
                await submit_button.scroll_into_view_if_needed()
                
                # Hover trước khi click
                await submit_button.hover()
                await asyncio.sleep(random.uniform(0.3, 0.8))
                
                # Click submit
                await submit_button.click(force=True)
                
                # Đợi phản hồi
                await target_page.wait_for_load_state('networkidle')
        
        except Exception as e:
            # Xử lý lỗi nếu có
            pass         
             
    async def simulate_mobile_behavior(self, page: Optional[AsyncPage] = None, duration: int = 30):
        """
        Mô phỏng đầy đủ các hành vi người dùng trên thiết bị di động.
        
        Args:
            page: Trang để thực hiện hành vi, mặc định là self.page
            duration: Thời gian tối đa dành cho việc mô phỏng (giây)
        """
        target_page = page if page else self.page
        
        try:
            # Lấy kích thước viewport
            viewport = await target_page.evaluate("""
                () => {
                    return {
                        width: window.innerWidth,
                        height: window.innerHeight
                    }
                }
            """)
            width, height = viewport['width'], viewport['height']
            
            # Sửa lỗi trong phương thức gốc - cần thêm đợi sau tap
            async def perform_tap(x, y):
                await target_page.touchscreen.tap(x, y)
                await asyncio.sleep(random.uniform(0.3, 1.0))
            
            # Thiết lập thời gian bắt đầu
            start_time = time.time()
            
            # Mô phỏng các hành vi di động cho đến khi hết thời gian
            while time.time() - start_time < duration:
                # Chọn hành vi ngẫu nhiên để thực hiện
                behavior = random.choices(
                    ['swipe', 'zoom', 'tap', 'rotate', 'scroll', 'pause'],
                    weights=[0.4, 0.15, 0.25, 0.05, 0.1, 0.05],
                    k=1
                )[0]
                
                # 1. Mô phỏng vuốt (swipe)
                if behavior == 'swipe':
                    # Xác định hướng vuốt: lên, xuống, trái, phải
                    swipe_direction = random.choice(['up', 'down', 'left', 'right'])
                    
                    # Điểm bắt đầu vuốt
                    if swipe_direction in ['up', 'down']:
                        start_x = random.uniform(width * 0.2, width * 0.8)
                        start_y = random.uniform(height * 0.3, height * 0.7) if swipe_direction == 'up' else random.uniform(height * 0.3, height * 0.5)
                    else:  # trái, phải
                        start_x = random.uniform(width * 0.7, width * 0.9) if swipe_direction == 'left' else random.uniform(width * 0.1, width * 0.3)
                        start_y = random.uniform(height * 0.3, height * 0.7)
                    
                    # Điểm kết thúc vuốt
                    if swipe_direction == 'up':
                        end_x = start_x + random.uniform(-30, 30)
                        end_y = start_y - random.uniform(height * 0.3, height * 0.5)
                    elif swipe_direction == 'down':
                        end_x = start_x + random.uniform(-30, 30)
                        end_y = start_y + random.uniform(height * 0.3, height * 0.5)
                    elif swipe_direction == 'left':
                        end_x = start_x - random.uniform(width * 0.4, width * 0.6)
                        end_y = start_y + random.uniform(-30, 30)
                    else:  # right
                        end_x = start_x + random.uniform(width * 0.4, width * 0.6)
                        end_y = start_y + random.uniform(-30, 30)
                    
                    # Kiểm tra xem điểm kết thúc có nằm trong viewport không
                    end_x = max(10, min(width - 10, end_x))
                    end_y = max(10, min(height - 10, end_y))
                    
                    # Bắt đầu chạm
                    await target_page.touchscreen.tap(start_x, start_y)
                    await asyncio.sleep(random.uniform(0.05, 0.15))  # Chờ một chút
                    
                    # Thực hiện vuốt
                    steps = random.randint(5, 15)
                    for i in range(1, steps + 1):
                        progress = i / steps
                        # Sử dụng hàm easing để tạo chuyển động mượt mà
                        eased_progress = -math.cos(progress * math.pi) / 2 + 0.5
                        
                        current_x = start_x + (end_x - start_x) * eased_progress
                        current_y = start_y + (end_y - start_y) * eased_progress
                        
                        # Mô phỏng di chuyển ngón tay
                        await target_page.mouse.move(current_x, current_y)
                        await asyncio.sleep(random.uniform(0.01, 0.03))
                    
                    # Kết thúc chạm
                    await target_page.mouse.up()
                    
                    # Đợi trang cuộn xong
                    await asyncio.sleep(random.uniform(1.0, 2.5))
                    
                    # Đôi khi thực hiện một vuốt ngược lại
                    if random.random() < 0.3:
                        # Vuốt ngược lại
                        reverse_x = end_x + random.uniform(-20, 20)
                        reverse_y = end_y + random.uniform(-20, 20)
                        
                        # Điểm kết thúc của vuốt ngược
                        reverse_end_x = start_x + random.uniform(-30, 30)
                        reverse_end_y = start_y + random.uniform(-30, 30)
                        
                        # Thực hiện vuốt ngược lại
                        await target_page.touchscreen.tap(reverse_x, reverse_y)
                        await asyncio.sleep(random.uniform(0.05, 0.15))
                        
                        steps = random.randint(5, 10)
                        for i in range(1, steps + 1):
                            progress = i / steps
                            eased_progress = -math.cos(progress * math.pi) / 2 + 0.5
                            
                            current_x = reverse_x + (reverse_end_x - reverse_x) * eased_progress
                            current_y = reverse_y + (reverse_end_y - reverse_y) * eased_progress
                            
                            await target_page.mouse.move(current_x, current_y)
                            await asyncio.sleep(random.uniform(0.01, 0.03))
                        
                        await target_page.mouse.up()
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                        
                # 2. Mô phỏng zoom bằng hai ngón tay
                elif behavior == 'zoom':
                    # Chọn loại zoom: zoom in hoặc zoom out
                    zoom_type = random.choice(['in', 'out'])
                    center_x = random.uniform(width * 0.3, width * 0.7)
                    center_y = random.uniform(height * 0.3, height * 0.7)
                    
                    # Khoảng cách ban đầu giữa các ngón tay
                    initial_distance = random.randint(50, 120)
                    # Khoảng cách cuối cùng (rộng hơn nếu zoom in, gần hơn nếu zoom out)
                    final_distance = initial_distance * (random.uniform(1.5, 2.5) if zoom_type == 'in' else random.uniform(0.3, 0.7))
                    
                    # Thực hiện pinch zoom
                    await target_page.evaluate(f"""
                        () => {{
                            // Tọa độ cho ngón tay thứ nhất
                            const f1StartX = {center_x - initial_distance/2};
                            const f1StartY = {center_y - initial_distance/2};
                            const f1EndX = {center_x - final_distance/2};
                            const f1EndY = {center_y - final_distance/2};
                            
                            // Tọa độ cho ngón tay thứ hai
                            const f2StartX = {center_x + initial_distance/2};
                            const f2StartY = {center_y + initial_distance/2};
                            const f2EndX = {center_x + final_distance/2};
                            const f2EndY = {center_y + final_distance/2};
                            
                            // Tạo sự kiện touch giả
                            const touchStart = new TouchEvent('touchstart', {{
                                bubbles: true,
                                touches: [
                                    new Touch({{
                                        identifier: 0,
                                        target: document.body,
                                        clientX: f1StartX,
                                        clientY: f1StartY
                                    }}),
                                    new Touch({{
                                        identifier: 1,
                                        target: document.body,
                                        clientX: f2StartX,
                                        clientY: f2StartY
                                    }})
                                ]
                            }});
                            
                            const touchMove = new TouchEvent('touchmove', {{
                                bubbles: true,
                                touches: [
                                    new Touch({{
                                        identifier: 0,
                                        target: document.body,
                                        clientX: f1EndX,
                                        clientY: f1EndY
                                    }}),
                                    new Touch({{
                                        identifier: 1,
                                        target: document.body,
                                        clientX: f2EndX,
                                        clientY: f2EndY
                                    }})
                                ]
                            }});
                            
                            const touchEnd = new TouchEvent('touchend', {{
                                bubbles: true,
                                touches: []
                            }});
                            
                            document.body.dispatchEvent(touchStart);
                            
                            // Đợi một chút trước khi move
                            setTimeout(() => {{
                                document.body.dispatchEvent(touchMove);
                                
                                // Đợi một chút trước khi kết thúc
                                setTimeout(() => {{
                                    document.body.dispatchEvent(touchEnd);
                                }}, {int(random.uniform(100, 300))});
                            }}, {int(random.uniform(50, 150))});
                        }}
                    """)
                    
                    # Đợi một chút sau khi zoom
                    await asyncio.sleep(random.uniform(1.0, 3.0))
                    
                    # Đôi khi thực hiện zoom ngược lại
                    if random.random() < 0.4:
                        # Đổi loại zoom
                        zoom_type = 'in' if zoom_type == 'out' else 'out'
                        reversed_final_distance = initial_distance * (random.uniform(1.5, 2.5) if zoom_type == 'in' else random.uniform(0.3, 0.7))
                        
                        await target_page.evaluate(f"""
                            () => {{
                                const f1StartX = {center_x - final_distance/2};
                                const f1StartY = {center_y - final_distance/2};
                                const f1EndX = {center_x - reversed_final_distance/2};
                                const f1EndY = {center_y - reversed_final_distance/2};
                                
                                const f2StartX = {center_x + final_distance/2};
                                const f2StartY = {center_y + final_distance/2};
                                const f2EndX = {center_x + reversed_final_distance/2};
                                const f2EndY = {center_y + reversed_final_distance/2};
                                
                                const touchStart = new TouchEvent('touchstart', {{
                                    bubbles: true,
                                    touches: [
                                        new Touch({{
                                            identifier: 0,
                                            target: document.body,
                                            clientX: f1StartX,
                                            clientY: f1StartY
                                        }}),
                                        new Touch({{
                                            identifier: 1,
                                            target: document.body,
                                            clientX: f2StartX,
                                            clientY: f2StartY
                                        }})
                                    ]
                                }});
                                
                                const touchMove = new TouchEvent('touchmove', {{
                                    bubbles: true,
                                    touches: [
                                        new Touch({{
                                            identifier: 0,
                                            target: document.body,
                                            clientX: f1EndX,
                                            clientY: f1EndY
                                        }}),
                                        new Touch({{
                                            identifier: 1,
                                            target: document.body,
                                            clientX: f2EndX,
                                            clientY: f2EndY
                                        }})
                                    ]
                                }});
                                
                                const touchEnd = new TouchEvent('touchend', {{
                                    bubbles: true,
                                    touches: []
                                }});
                                
                                document.body.dispatchEvent(touchStart);
                                setTimeout(() => {{
                                    document.body.dispatchEvent(touchMove);
                                    setTimeout(() => {{
                                        document.body.dispatchEvent(touchEnd);
                                    }}, {int(random.uniform(100, 300))});
                                }}, {int(random.uniform(50, 150))});
                            }}
                        """)
                        
                        await asyncio.sleep(random.uniform(1.0, 2.0))
                
                # 3. Mô phỏng tap vào các phần tử
                elif behavior == 'tap':
                    # Chọn phần tử dễ tương tác
                    selectors = ["a", "button", ".card", ".item", "li", ".product", 
                                "[role=button]", "[tabindex]", ".menu-item", ".nav-item"]
                    try:
                        for _ in range(random.randint(1, 3)):
                            selector = random.choice(selectors)
                            elements = await target_page.query_selector_all(selector)
                            
                            if elements and len(elements) > 0:
                                # Chọn một phần tử ngẫu nhiên từ danh sách
                                random_idx = random.randint(0, min(len(elements)-1, 15))  # Giới hạn ở 15 phần tử đầu tiên
                                random_element = elements[random_idx]
                                
                                # Đảm bảo phần tử nhìn thấy được
                                is_visible = await target_page.evaluate("""
                                    (element) => {
                                        const rect = element.getBoundingClientRect();
                                        return rect.width > 0 && 
                                            rect.height > 0 && 
                                            rect.top < window.innerHeight &&
                                            rect.left < window.innerWidth &&
                                            rect.bottom > 0 &&
                                            rect.right > 0 &&
                                            window.getComputedStyle(element).visibility !== 'hidden' &&
                                            window.getComputedStyle(element).display !== 'none';
                                    }
                                """, random_element)
                                
                                if is_visible:
                                    # Cuộn đến phần tử
                                    await random_element.scroll_into_view_if_needed()
                                    await asyncio.sleep(random.uniform(0.5, 1.0))
                                    
                                    # Lấy vị trí phần tử
                                    box = await random_element.bounding_box()
                                    if box:
                                        # Tap tại vị trí ngẫu nhiên trong phần tử
                                        tap_x = box['x'] + random.uniform(box['width'] * 0.2, box['width'] * 0.8)
                                        tap_y = box['y'] + random.uniform(box['height'] * 0.2, box['height'] * 0.8)
                                        
                                        # Thực hiện tap
                                        await perform_tap(tap_x, tap_y)
                                        
                                        # Đợi trang phản hồi
                                        try:
                                            await target_page.wait_for_load_state('networkidle', timeout=5000)
                                        except:
                                            pass
                                        
                                        # Đôi khi quay lại bằng nút back
                                        if random.random() < 0.3:
                                            try:
                                                history_len = await target_page.evaluate("window.history.length")
                                                if history_len > 1:
                                                    await target_page.go_back()
                                                    await target_page.wait_for_load_state('domcontentloaded')
                                            except:
                                                pass
                    except Exception as e:
                        pass
                        
                # 4. Mô phỏng xoay thiết bị
                elif behavior == 'rotate':
                    # Chỉ xoay trong 20% trường hợp
                    current_orientation = await target_page.evaluate("""
                        () => window.screen && window.screen.orientation ? 
                        window.screen.orientation.type : 'portrait-primary'
                    """)
                    
                    new_orientation = 'portrait-primary' if 'landscape' in current_orientation else 'landscape-primary'
                    
                    # Mô phỏng xoay thiết bị
                    await target_page.evaluate(f"""
                        () => {{
                            // Cập nhật window.orientation (API cũ)
                            Object.defineProperty(window, 'orientation', {{
                                get: function() {{ 
                                    return {90 if 'landscape' in new_orientation else 0}; 
                                }}
                            }});
                            
                            // Giả lập sự kiện orientationchange
                            const event = new Event('orientationchange');
                            window.dispatchEvent(event);
                            
                            // Cập nhật window.screen.orientation (API mới)
                            if (window.screen && window.screen.orientation) {{
                                Object.defineProperty(window.screen.orientation, 'type', {{
                                    get: function() {{ return '{new_orientation}'; }}
                                }});
                                
                                Object.defineProperty(window.screen.orientation, 'angle', {{
                                    get: function() {{ return {90 if 'landscape' in new_orientation else 0}; }}
                                }});
                                
                                // Giả lập sự kiện change cho orientation
                                const orientationEvent = new Event('change');
                                window.screen.orientation.dispatchEvent(orientationEvent);
                            }}
                            
                            // Giả lập thay đổi kích thước màn hình
                            const resizeEvent = new Event('resize');
                            window.dispatchEvent(resizeEvent);
                        }}
                    """)
                    
                    # Chờ để trang phản hồi với hướng mới
                    await asyncio.sleep(random.uniform(2.0, 4.0))
                
                # 5. Mô phỏng cuộn trang
                elif behavior == 'scroll':
                    # Đôi khi thực hiện cuộn động với tác động quán tính
                    scroll_distance = random.randint(300, 800)
                    scroll_direction = random.choice(['down', 'up'])
                    scroll_multiplier = 1 if scroll_direction == 'down' else -1
                    
                    # Mô phỏng cuộn với gia tốc và giảm tốc
                    steps = random.randint(10, 20)
                    total_scroll = 0
                    
                    # Tạo mẫu cuộn có gia tốc và giảm tốc
                    for i in range(steps):
                        progress = i / (steps - 1)
                        # Tạo đường cong: tăng tốc ở đầu, giảm tốc ở cuối
                        if progress < 0.3:
                            # Pha tăng tốc
                            factor = progress / 0.3
                        elif progress > 0.7:
                            # Pha giảm tốc
                            factor = (1 - progress) / 0.3
                        else:
                            # Pha giữ tốc độ
                            factor = 1.0
                        
                        # Tính khoảng cuộn cho bước này
                        scroll_step = int((scroll_distance / steps) * factor) * scroll_multiplier
                        total_scroll += scroll_step
                        
                        # Thực hiện cuộn
                        await target_page.evaluate(f"window.scrollBy(0, {scroll_step})")
                        await asyncio.sleep(random.uniform(0.05, 0.12))
                    
                    # Đôi khi thêm "quán tính" sau khi cuộn
                    if random.random() < 0.4:
                        overshoot_steps = random.randint(2, 5)
                        for i in range(overshoot_steps):
                            # Tạo hiệu ứng quán tính (nhỏ dần và đổi chiều)
                            inertia_step = int((scroll_distance / 10) * ((overshoot_steps - i) / overshoot_steps) 
                                            * (1 if i % 2 == 0 else -1) * 0.2) * scroll_multiplier
                            
                            await target_page.evaluate(f"window.scrollBy(0, {inertia_step})")
                            await asyncio.sleep(random.uniform(0.1, 0.2))
                    
                    # Đợi sau khi cuộn
                    await asyncio.sleep(random.uniform(1.0, 2.5))
                    
                    # Đôi khi đọc nội dung sau khi cuộn
                    if random.random() < 0.5:
                        # Mô phỏng đọc bằng cách để dừng một khoảng thời gian
                        await asyncio.sleep(random.uniform(2.0, 5.0))
                
                # 6. Mô phỏng tạm dừng (đọc nội dung)
                elif behavior == 'pause':
                    # Mô phỏng việc đọc nội dung
                    pause_time = random.uniform(3.0, 8.0)
                    await asyncio.sleep(pause_time)
                    
                    # Thỉnh thoảng thực hiện vuốt chậm để đọc tiếp
                    if random.random() < 0.5:
                        slow_scroll_distance = random.randint(50, 150)
                        slow_scroll_steps = random.randint(8, 15)
                        
                        for _ in range(slow_scroll_steps):
                            step = int(slow_scroll_distance / slow_scroll_steps)
                            await target_page.evaluate(f"window.scrollBy(0, {step})")
                            await asyncio.sleep(random.uniform(0.2, 0.5))
                    
            return True
        
        except Exception as e:
            raise Exception(f"Error in simulate_mobile_behavior: {e}")
    
    async def simulate_social_media_behavior(self, page: Optional[AsyncPage] = None, duration: int = 60):
        """
        Mô phỏng hành vi duyệt mạng xã hội như một người dùng thật
        
        Args:
            page: Trang để thực hiện hành vi, mặc định là self.page
            duration: Thời gian tối đa dành cho việc mô phỏng (giây)
        """
        target_page = page if page else self.page
        
        start_time = time.time()
        
        try:
            # Xác định loại mạng xã hội (có thể mở rộng cho các mạng khác)
            is_facebook = await target_page.evaluate("""
                () => window.location.href.includes('facebook.com')
            """)
            
            is_instagram = await target_page.evaluate("""
                () => window.location.href.includes('instagram.com')
            """)
            
            is_twitter = await target_page.evaluate("""
                () => window.location.href.includes('twitter.com') || 
                    window.location.href.includes('x.com')
            """)
            
            is_tiktok = await target_page.evaluate("""
                () => window.location.href.includes('tiktok.com')
            """)
            
            is_linkedin = await target_page.evaluate("""
                () => window.location.href.includes('linkedin.com')
            """)
            
            is_youtube = await target_page.evaluate("""
                () => window.location.href.includes('youtube.com')
            """)
            
            # Cấu hình selector cho từng mạng xã hội
            post_selectors = []
            like_selectors = []
            comment_selectors = []
            share_selectors = []
            feed_scroll_selector = "body"
            story_selectors = []
            
            if is_facebook:
                post_selectors = ["div[role='article']", ".x1yztbdb", "[data-ad-preview='message']"]
                like_selectors = ["[aria-label*='Like']", "[aria-label*='thích']"]
                comment_selectors = ["[aria-label*='Comment']", "[aria-label*='bình luận']"]
                share_selectors = ["[aria-label*='Send']", "[aria-label*='Share']", "[aria-label*='chia sẻ']"]
                story_selectors = [".x1i10hfl[role='button']", ".xukrpv[role='button']"]
                feed_scroll_selector = "div[role='feed']"
                
            elif is_instagram:
                post_selectors = ["article", "._aatb", "._ab6k"]
                like_selectors = ["[aria-label*='Like']", "._aamw button", "._abl-"]
                comment_selectors = ["[aria-label*='Comment']", "._aao9"]
                story_selectors = [".x1i10hfl", "._aac4._aac5._aac6"]
                
            elif is_twitter:
                post_selectors = ["article", "[data-testid='tweet']", ".css-1dbjc4n"]
                like_selectors = ["[data-testid='like']", "[aria-label*='Like']"]
                comment_selectors = ["[data-testid='reply']", "[aria-label*='Reply']"]
                share_selectors = ["[data-testid='retweet']", "[aria-label*='Retweet']"]
                
            elif is_tiktok:
                post_selectors = [".tiktok-1soki6-DivItemContainer", ".tiktok-x6y88p-DivItemContainerV2"]
                like_selectors = [".tiktok-1kw58wa", "[data-e2e='like-icon']"]
                comment_selectors = [".tiktok-bvxsci", "[data-e2e='comment-icon']"]
                share_selectors = [".tiktok-3q85cl", "[data-e2e='share-icon']"]
                
            elif is_linkedin:
                post_selectors = [".feed-shared-update-v2", ".update-components-actor"]
                like_selectors = ["button.react-button__trigger", "[aria-label*='Like']", "[aria-label*='reaction']"]
                comment_selectors = ["button.comment-button", "[aria-label*='Comment']"]
                share_selectors = ["button.share-button", "[aria-label*='Share']"]
                
            elif is_youtube:
                post_selectors = ["ytd-video-renderer", "ytd-compact-video-renderer"]
                like_selectors = ["button[aria-label*='like']", "ytd-toggle-button-renderer"]
                comment_selectors = ["#comments", "ytd-comment-renderer"]
                
            else:
                # Generic selectors cho các trang khác
                post_selectors = ["article", ".post", ".card", ".feed-item", ".stream-item"]
                like_selectors = ["[aria-label*='Like']", "[aria-label*='like']", ".like-button", ".fav-button"]
                comment_selectors = ["[aria-label*='Comment']", "[aria-label*='comment']", ".comment-button", ".reply-button"]
                share_selectors = ["[aria-label*='Share']", "[aria-label*='share']", ".share-button", ".retweet-button"]
            
            # Tạo bình luận ngẫu nhiên nếu cần
            comments_pool = [
                "Thú vị quá!", "Rất hay!", "Cảm ơn bạn đã chia sẻ", 
                "Tôi thích điều này", "Thật thú vị!", "Rất tuyệt!",
                "Tôi cũng đang nghĩ vậy", "Hoàn toàn đồng ý", 
                "Chia sẻ hay quá", "Cảm ơn thông tin"
            ]
            
            # Mô phỏng các hành vi mạng xã hội cho đến khi hết thời gian
            while time.time() - start_time < duration:
                # Chọn hành vi ngẫu nhiên để thực hiện
                behavior = random.choices(
                    ['scroll', 'like', 'view_post', 'comment', 'share', 'view_story', 'pause'],
                    weights=[0.5, 0.15, 0.15, 0.05, 0.05, 0.05, 0.05],  # Scroll là hành vi phổ biến nhất
                    k=1
                )[0]
                
                if behavior == 'scroll':
                    # Cuộn xuống feed với tốc độ khác nhau
                    scroll_amount = random.randint(300, 800)
                    await target_page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                    
                    # Đôi khi tạm dừng để xem nội dung
                    if random.random() < 0.3:
                        await asyncio.sleep(random.uniform(1.0, 3.0))
                    else:
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                        
                elif behavior == 'like':
                    # Tìm các nút like có thể click
                    for selector in like_selectors:
                        try:
                            like_buttons = await target_page.query_selector_all(selector)
                            if like_buttons and len(like_buttons) > 0:
                                # Chọn một nút like ngẫu nhiên từ các nút đầu tiên hiển thị
                                visible_buttons = []
                                for button in like_buttons[:10]:
                                    is_visible = await button.is_visible()
                                    if is_visible:
                                        visible_buttons.append(button)
                                
                                if visible_buttons:
                                    # Chỉ thỉnh thoảng like (30% xác suất)
                                    if random.random() < 0.3:
                                        random_button = random.choice(visible_buttons)
                                        await random_button.scroll_into_view_if_needed()
                                        
                                        # Di chuyển chuột đến nút like một cách tự nhiên
                                        box = await random_button.bounding_box()
                                        if box:
                                            await self.perform_human_like_mouse_movements(target_page, 
                                                                                        num_points=3)
                                            await target_page.mouse.move(
                                                box['x'] + box['width'] / 2,
                                                box['y'] + box['height'] / 2
                                            )
                                            await asyncio.sleep(random.uniform(0.2, 0.5))
                                            
                                            # Click vào nút like
                                            await target_page.mouse.click(
                                                box['x'] + box['width'] / 2,
                                                box['y'] + box['height'] / 2
                                            )
                                            
                                            # Đôi khi xem menu reaction
                                            if is_facebook and random.random() < 0.2:
                                                await asyncio.sleep(random.uniform(0.8, 1.5))
                                                # Chọn một reaction khác
                                                reactions = await target_page.query_selector_all("[aria-label*='reaction']")
                                                if reactions and len(reactions) > 0:
                                                    random_reaction = random.choice(reactions)
                                                    await random_reaction.click(force=True)
                                            
                                            await asyncio.sleep(random.uniform(0.5, 1.2))
                                            break
                        except Exception as e:
                            continue
                            
                elif behavior == 'view_post':
                    # Mở một bài đăng ngẫu nhiên để xem chi tiết
                    for selector in post_selectors:
                        try:
                            posts = await target_page.query_selector_all(selector)
                            if posts and len(posts) > 0:
                                # Chọn một bài đăng ngẫu nhiên từ các bài đăng có sẵn
                                visible_posts = []
                                for post in posts[:10]:
                                    is_visible = await post.is_visible()
                                    if is_visible:
                                        visible_posts.append(post)
                                
                                if visible_posts:
                                    random_post = random.choice(visible_posts)
                                    await random_post.scroll_into_view_if_needed()
                                    
                                    # Đôi khi đọc trước nội dung bài đăng
                                    if random.random() < 0.7:
                                        await asyncio.sleep(random.uniform(1.5, 4.0))
                                    
                                    # Click vào bài đăng (hoặc một phần tử con của nó)
                                    try:
                                        # Tìm một phần tử có thể click trong bài đăng
                                        clickable_elements = await random_post.query_selector_all("a, [role='link'], [role='button']")
                                        if clickable_elements and len(clickable_elements) > 0:
                                            random_element = random.choice(clickable_elements)
                                            await random_element.click(force=True)
                                        else:
                                            await random_post.click(force=True)
                                            
                                        # Đợi bài đăng/trang chi tiết mở ra
                                        await target_page.wait_for_load_state('networkidle')
                                        
                                        # Mô phỏng đọc nội dung bài đăng
                                        await self.simulate_reading_behavior(target_page, 
                                                                        min_read_time=8, 
                                                                        max_read_time=20)
                                        
                                        # Tương tác trong bài đăng
                                        if random.random() < 0.3:
                                            # Có thể like hoặc comment trong bài đăng chi tiết
                                            if random.random() < 0.7:
                                                like_in_detail = await target_page.query_selector_all(like_selectors[0])
                                                if like_in_detail and len(like_in_detail) > 0:
                                                    await like_in_detail[0].click(force=True)
                                                    await asyncio.sleep(random.uniform(0.5, 1.0))
                                        
                                        # Quay lại trang chính
                                        await target_page.go_back()
                                        await target_page.wait_for_load_state('networkidle')
                                    except Exception as e:
                                        # Bỏ qua lỗi và tiếp tục
                                        continue
                                    
                                    break
                        except Exception as e:
                            continue
                            
                elif behavior == 'comment':
                    # Chỉ comment với xác suất thấp (để tránh spam)
                    if random.random() < 0.15:
                        for selector in comment_selectors:
                            try:
                                comment_buttons = await target_page.query_selector_all(selector)
                                if comment_buttons and len(comment_buttons) > 0:
                                    # Chọn một comment button ngẫu nhiên
                                    visible_buttons = []
                                    for button in comment_buttons[:10]:
                                        is_visible = await button.is_visible()
                                        if is_visible:
                                            visible_buttons.append(button)
                                    
                                    if visible_buttons:
                                        random_button = random.choice(visible_buttons)
                                        await random_button.scroll_into_view_if_needed()
                                        await random_button.click(force=True)
                                        
                                        # Đợi form comment xuất hiện
                                        await asyncio.sleep(random.uniform(0.8, 1.5))
                                        
                                        # Tìm ô nhập comment
                                        comment_input_selectors = [
                                            "textarea", 
                                            "[contenteditable='true']", 
                                            "[aria-label*='comment']", 
                                            "[aria-label*='Write']",
                                            "[aria-label*='viết']",
                                            "[placeholder*='comment']",
                                            "[placeholder*='bình luận']"
                                        ]
                                        
                                        for input_selector in comment_input_selectors:
                                            comment_input = await target_page.query_selector(input_selector)
                                            if comment_input:
                                                # Chọn một bình luận ngẫu nhiên
                                                comment_text = random.choice(comments_pool)
                                                
                                                # Nhập bình luận như người dùng thật
                                                await comment_input.click(force=True)
                                                await asyncio.sleep(random.uniform(0.3, 0.7))
                                                
                                                # Nhập từng ký tự với tốc độ khác nhau
                                                for i, char in enumerate(comment_text):
                                                    # Tạo độ trễ ngẫu nhiên giữa các ký tự
                                                    if i > 0:
                                                        # Tạo độ trễ dài hơn ở giữa các từ
                                                        if comment_text[i-1] == ' ':
                                                            await asyncio.sleep(random.uniform(0.3, 0.7))
                                                        else:
                                                            typing_speed = random.normalvariate(0.1, 0.05)
                                                            await asyncio.sleep(max(0.05, min(0.3, typing_speed)))
                                                    
                                                    # Đôi khi gõ sai và sửa lại
                                                    if random.random() < 0.05 and char.isalpha():
                                                        typo_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                                                        await target_page.keyboard.type(typo_char)
                                                        await asyncio.sleep(random.uniform(0.1, 0.3))
                                                        await target_page.keyboard.press('Backspace')
                                                        await asyncio.sleep(random.uniform(0.1, 0.2))
                                                    
                                                    # Gõ ký tự
                                                    await target_page.keyboard.type(char)
                                                
                                                # Đôi khi đọc lại bình luận trước khi đăng
                                                if random.random() < 0.3:
                                                    await asyncio.sleep(random.uniform(1.0, 2.0))
                                                
                                                # Nhấn Enter để gửi
                                                await asyncio.sleep(random.uniform(0.3, 0.8))
                                                await target_page.keyboard.press('Enter')
                                                
                                                # Đợi bình luận được gửi đi
                                                await asyncio.sleep(random.uniform(1.0, 2.0))
                                                break
                                        
                                        break
                            except Exception as e:
                                continue
                                
                elif behavior == 'share':
                    # Chỉ share với xác suất thấp
                    if random.random() < 0.1 and share_selectors:
                        for selector in share_selectors:
                            try:
                                share_buttons = await target_page.query_selector_all(selector)
                                if share_buttons and len(share_buttons) > 0:
                                    # Chọn một nút share ngẫu nhiên
                                    visible_buttons = []
                                    for button in share_buttons[:10]:
                                        is_visible = await button.is_visible()
                                        if is_visible:
                                            visible_buttons.append(button)
                                    
                                    if visible_buttons:
                                        random_button = random.choice(visible_buttons)
                                        await random_button.scroll_into_view_if_needed()
                                        await random_button.click(force=True)
                                        
                                        # Đợi dialog share hiện ra
                                        await asyncio.sleep(random.uniform(1.0, 2.0))
                                        
                                        if is_facebook:
                                            # Trên Facebook, nhấp vào nút "Chia sẻ ngay"
                                            share_now_button = await target_page.query_selector(
                                                "[aria-label*='Share Now']"
                                            )
                                            if share_now_button:
                                                await share_now_button.click(force=True)
                                                await asyncio.sleep(random.uniform(1.0, 2.0))
                                        elif is_twitter:
                                            # Trên Twitter, có thể thêm nội dung trước khi retweet
                                            retweet_button = await target_page.query_selector(
                                                "[data-testid='retweetConfirm']"
                                            )
                                            if retweet_button:
                                                await retweet_button.click(force=True)
                                                await asyncio.sleep(random.uniform(1.0, 2.0))
                                        else:
                                            # Đối với các mạng xã hội khác, thường có nút đóng
                                            close_button = await target_page.query_selector(
                                                "[aria-label='Close'], .close-button, button.cancel"
                                            )
                                            if close_button:
                                                await close_button.click(force=True)
                                        
                                        break
                            except Exception as e:
                                continue
                                
                elif behavior == 'view_story':
                    # Xem stories nếu có (phổ biến trên Facebook, Instagram)
                    if story_selectors and (is_facebook or is_instagram):
                        for selector in story_selectors:
                            try:
                                story_buttons = await target_page.query_selector_all(selector)
                                if story_buttons and len(story_buttons) > 0:
                                    visible_stories = []
                                    for story in story_buttons[:10]:
                                        is_visible = await story.is_visible()
                                        if is_visible:
                                            visible_stories.append(story)
                                    
                                    if visible_stories:
                                        # Chọn một story ngẫu nhiên
                                        random_story = random.choice(visible_stories)
                                        await random_story.scroll_into_view_if_needed()
                                        await random_story.click(force=True)
                                        
                                        # Đợi story load
                                        await asyncio.sleep(random.uniform(1.0, 2.0))
                                        
                                        # Mô phỏng xem nhiều stories liên tiếp
                                        num_stories = random.randint(1, 5)
                                        for _ in range(num_stories):
                                            # Xem mỗi story từ 2-5 giây
                                            await asyncio.sleep(random.uniform(2.0, 5.0))
                                            
                                            # Đôi khi phản ứng với story
                                            if random.random() < 0.2:
                                                # Tìm nút reaction trên story
                                                reaction_buttons = await target_page.query_selector_all(
                                                    "[aria-label*='React'], [aria-label*='reaction']"
                                                )
                                                if reaction_buttons and len(reaction_buttons) > 0:
                                                    await random.choice(reaction_buttons).click(force=True)
                                                    await asyncio.sleep(random.uniform(0.5, 1.0))
                                            
                                            # Click để chuyển sang story tiếp theo
                                            viewport_size = await target_page.evaluate("""
                                                () => ({
                                                    width: window.innerWidth,
                                                    height: window.innerHeight
                                                })
                                            """)
                                            await target_page.mouse.click(
                                                viewport_size['width'] * 0.9, 
                                                viewport_size['height'] * 0.5
                                            )
                                        
                                        # Đóng stories
                                        if random.random() < 0.7:
                                            # Thường đóng bằng nút đóng
                                            close_buttons = await target_page.query_selector_all(
                                                "[aria-label='Close'], .close-button, [aria-label*='Đóng']"
                                            )
                                            if close_buttons and len(close_buttons) > 0:
                                                await random.choice(close_buttons).click(force=True)
                                            else:
                                                # Nhấn Escape để đóng
                                                await target_page.keyboard.press('Escape')
                                        
                                        await asyncio.sleep(random.uniform(1.0, 2.0))
                                        break
                            except Exception as e:
                                continue
                                    
                elif behavior == 'pause':
                    # Mô phỏng tạm dừng để đọc nội dung
                    pause_time = random.uniform(2.0, 5.0)
                    await asyncio.sleep(pause_time)
                    
                    # Mô phỏng di chuyển mắt (di chuyển chuột nhẹ nhàng)
                    try:
                        current_pos = await target_page.evaluate("""
                            () => ({ x: window.innerWidth/2, y: window.innerHeight/2 })
                        """)
                        
                        current_x = current_pos['x']
                        current_y = current_pos['y']
                        
                        # Di chuyển chuột nhẹ nhàng như đang đọc
                        for _ in range(3):
                            offset_x = random.uniform(-50, 50)
                            offset_y = random.uniform(-30, 30)
                            await target_page.mouse.move(
                                current_x + offset_x,
                                current_y + offset_y
                            )
                            await asyncio.sleep(random.uniform(0.3, 0.7))
                    except Exception as e:
                        pass
            
            return True
        
        except Exception as e:
            raise Exception(f"Error in simulate_social_media_behavior: {e}")

    async def add_browser_fingerprint_evasions(self, level: str = "high"):
        """
        Thêm các script để ngụy trang fingerprint trình duyệt
        
        Args:
            level: Mức độ ngụy trang ("basic", "standard", "high", "extreme")
        """
        # Script cơ bản - chỉ vô hiệu hóa webdriver
        try:
            basic_script = """
            () => {
                // Ghi đè navigator.webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false
                });
            }
            """
            
            # Script tiêu chuẩn - thêm một số thuộc tính phổ biến
            standard_script = """
            () => {
                // Cơ bản + vô hiệu hóa các thuộc tính tiêu chuẩn
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false
                });
                
                // Thêm plugins giả
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {
                        const plugins = [
                            { name: 'PDF Viewer', filename: 'internal-pdf-viewer' },
                            { name: 'Chrome PDF Viewer', filename: 'internal-pdf-viewer' },
                            { name: 'Chromium PDF Viewer', filename: 'internal-pdf-viewer' },
                            { name: 'Microsoft Edge PDF Viewer', filename: 'internal-pdf-viewer' },
                            { name: 'WebKit built-in PDF', filename: 'internal-pdf-viewer' }
                        ];
                        plugins.__proto__ = PluginArray.prototype;
                        return plugins;
                    }
                });
                
                // Thêm ngôn ngữ
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Ghi đè permissions.query
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            }
            """
            
            # Script cao cấp - thêm các kỹ thuật chống fingerprinting
            high_script = """
            () => {
                // --- Basic Evasions ---
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false
                });
                
                // --- Plugin & Browser Features ---
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {
                        const plugins = [
                            {
                                0: {type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format'},
                                name: 'PDF Viewer',
                                description: 'Portable Document Format',
                                filename: 'internal-pdf-viewer'
                            },
                            {
                                0: {type: 'application/x-shockwave-flash', suffixes: 'swf', description: 'Shockwave Flash'},
                                name: 'Shockwave Flash',
                                description: 'Shockwave Flash 32.0 r0',
                                filename: 'pepflashplayer.dll'
                            }
                        ];
                        plugins.__proto__ = PluginArray.prototype;
                        return plugins;
                    }
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // --- Canvas & WebGL Fingerprinting ---
                // Canvas fingerprinting
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type) {
                    if (type === 'image/png' && this.width === 16 && this.height === 16) {
                        // Thêm nhiễu nhỏ vào kết quả canvas fingerprinting
                        const data = originalToDataURL.call(this, type);
                        return data.substring(0, data.length - 8) + 
                            String.fromCharCode(
                                Math.floor(Math.random() * 16).toString(16) +
                                Math.floor(Math.random() * 16).toString(16) +
                                Math.floor(Math.random() * 16).toString(16) +
                                Math.floor(Math.random() * 16).toString(16)
                            );
                    }
                    return originalToDataURL.call(this, type);
                };
                
                // WebGL fingerprinting
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    // UNMASKED_VENDOR_WEBGL or UNMASKED_RENDERER_WEBGL
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    } else if (parameter === 37446) {
                        return 'Intel Iris Pro OpenGL Engine';
                    }
                    return getParameter.call(this, parameter);
                };
                
                // --- Media Devices ---
                if (window.navigator.mediaDevices && window.navigator.mediaDevices.enumerateDevices) {
                    const originalEnumerateDevices = window.navigator.mediaDevices.enumerateDevices;
                    window.navigator.mediaDevices.enumerateDevices = async () => {
                        const devices = await originalEnumerateDevices.call(window.navigator.mediaDevices);
                        if (!devices || devices.length === 0) {
                            return [
                                {
                                    deviceId: 'default',
                                    kind: 'audioinput',
                                    label: 'Default Audio Device',
                                    groupId: 'default'
                                },
                                {
                                    deviceId: 'default',
                                    kind: 'videoinput',
                                    label: 'Default Video Device',
                                    groupId: 'default'
                                }
                            ];
                        }
                        return devices;
                    };
                }
                
                // --- Permission Query ---
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            }
            """
            
            # Script cực cao - ngụy trang hoàn toàn + chống phân tích hành vi
            extreme_script = """
            () => {
                // Bao gồm tất cả từ high_script
                
                // --- Additional Protections ---
                
                // Chống phát hiện Automation framework
                window.navigator.chrome = { runtime: {} };
                window.chrome = { runtime: {} };
                
                // Thêm thuộc tính spoof để giấu bot
                Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
                Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
                Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 5});
                
                // Bot-detection counter measures
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10.0,
                        saveData: false
                    })
                });
                
                // Thêm thuộc tính window.chrome cần thiết
                window.chrome = {
                    app: {
                        InstallState: {
                            DISABLED: 'disabled',
                            INSTALLED: 'installed',
                            NOT_INSTALLED: 'not_installed'
                        },
                        RunningState: {
                            CANNOT_RUN: 'cannot_run',
                            READY_TO_RUN: 'ready_to_run',
                            RUNNING: 'running'
                        },
                        getDetails: function() {},
                        getIsInstalled: function() {},
                        installState: function() { 
                            return window.chrome.app.InstallState.INSTALLED;
                        },
                        isInstalled: false,
                        runningState: function() {
                            return window.chrome.app.RunningState.READY_TO_RUN;
                        }
                    },
                    runtime: {
                        OnInstalledReason: {
                            CHROME_UPDATE: 'chrome_update',
                            INSTALL: 'install',
                            SHARED_MODULE_UPDATE: 'shared_module_update',
                            UPDATE: 'update'
                        },
                        OnRestartRequiredReason: {
                            APP_UPDATE: 'app_update',
                            OS_UPDATE: 'os_update',
                            PERIODIC: 'periodic'
                        },
                        PlatformArch: {
                            ARM: 'arm',
                            ARM64: 'arm64',
                            MIPS: 'mips',
                            MIPS64: 'mips64',
                            X86_32: 'x86-32',
                            X86_64: 'x86-64'
                        },
                        PlatformNaclArch: {
                            ARM: 'arm',
                            MIPS: 'mips',
                            MIPS64: 'mips64',
                            X86_32: 'x86-32',
                            X86_64: 'x86-64'
                        },
                        PlatformOs: {
                            ANDROID: 'android',
                            CROS: 'cros',
                            LINUX: 'linux',
                            MAC: 'mac',
                            OPENBSD: 'openbsd',
                            WIN: 'win'
                        },
                        RequestUpdateCheckStatus: {
                            NO_UPDATE: 'no_update',
                            THROTTLED: 'throttled',
                            UPDATE_AVAILABLE: 'update_available'
                        }
                    }
                };
                
                // Chống phát hiện timing attack
                const originalPerformanceNow = window.performance.now;
                window.performance.now = function() {
                    const result = originalPerformanceNow.call(window.performance);
                    // Thêm nhiễu để tránh timing attack
                    return result + (Math.random() * 0.01);
                };
                
                // Chống theo dõi chuyển động chuột quá chính xác
                const originalMouseMove = MouseEvent.prototype.movementX;
                Object.defineProperty(MouseEvent.prototype, 'movementX', {
                    get: function() {
                        const value = originalMouseMove ? originalMouseMove.call(this) : 0;
                        return value + (Math.random() > 0.9 ? Math.random() * 2 - 1 : 0);
                    }
                });
                
                // Chống phát hiện qua AudioContext
                if (window.AudioContext) {
                    const originalGetChannelData = AudioBuffer.prototype.getChannelData;
                    AudioBuffer.prototype.getChannelData = function() {
                        const results = originalGetChannelData.apply(this, arguments);
                        // Chỉ sửa 0.1% mẫu âm thanh để không ảnh hưởng đến chất lượng
                        if (Math.random() < 0.0001) {
                            results[Math.floor(Math.random() * results.length)] += Math.random() * 0.0001;
                        }
                        return results;
                    }
                }
            }
            """
            
            # Chọn script phù hợp dựa trên level
            script_to_use = basic_script
            if level == "standard":
                script_to_use = standard_script
            elif level == "high":
                script_to_use = high_script
            elif level == "extreme":
                script_to_use = extreme_script
            
            # Thực thi script cho tất cả các trang mới
            await self.context.add_init_script(script_to_use) 
        except Exception as e:
            raise Exception(f"Error in add_browser_fingerprint_evasions: {e}")
     
    async def perform_human_like_mouse_movements(self, page: Optional[AsyncPage] = None, num_points: int = None):
        """
        Thực hiện các chuyển động chuột giống người dùng thật
        
        Args:
            page: Trang để thực hiện chuyển động, mặc định là self.page
            num_points: Số điểm điều khiển cho đường đi của chuột (mặc định ngẫu nhiên 5-10)
        """
        target_page: AsyncPage = page if page else self.page
        
        # Lấy kích thước viewport
        viewport = await target_page.evaluate('''
            () => {
                return {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
            }
        ''')
        width, height = viewport['width'], viewport['height']
        
        # Số điểm để tạo đường đi
        num_points = num_points or random.randint(5, 10)
        
        # Tạo đường cong Bezier cho chuyển động chuột tự nhiên
        points = []
        for _ in range(num_points):
            points.append({
                'x': random.randint(50, width - 50),
                'y': random.randint(50, height - 50),
                'pause': random.random() < 0.3  # Có khả năng dừng tại điểm này
            })
        
        # Vị trí hiện tại của chuột
        current_x, current_y = width / 2, height / 2
        
        # Di chuyển qua các điểm với tốc độ biến đổi
        for point in points:
            # Tính khoảng cách
            distance = math.sqrt((point['x'] - current_x) ** 2 + (point['y'] - current_y) ** 2)
            
            # Tạo điểm điều khiển cho đường cong Bezier
            control_x = (current_x + point['x']) / 2 + random.uniform(-distance/4, distance/4)
            control_y = (current_y + point['y']) / 2 + random.uniform(-distance/4, distance/4)
            
            # Số bước di chuyển dựa trên khoảng cách
            steps = max(10, min(30, int(distance / 10)))
            
            # Tốc độ thay đổi (chậm lại khi gần đích)
            for i in range(1, steps + 1):
                # Sử dụng t cho đường cong
                t = i / steps
                
                # Công thức đường cong Bezier bậc 2
                x = pow(1-t, 2) * current_x + 2 * (1-t) * t * control_x + pow(t, 2) * point['x']
                y = pow(1-t, 2) * current_y + 2 * (1-t) * t * control_y + pow(t, 2) * point['y']
                
                # Thêm độ run nhẹ
                if i > 1 and i < steps - 1:
                    x += random.uniform(-1, 1)
                    y += random.uniform(-1, 1)
                
                # Di chuyển chuột
                await target_page.mouse.move(x, y)
                
                # Tốc độ không đồng đều (chậm lại ở đầu và cuối)
                delay = 0.01
                if i < steps * 0.2 or i > steps * 0.8:
                    delay = random.uniform(0.015, 0.025)
                else:
                    delay = random.uniform(0.005, 0.015)
                    
                await asyncio.sleep(delay)
            
            current_x, current_y = point['x'], point['y']
            
            # Đôi khi dừng lại tại một số điểm
            if point['pause']:
                await asyncio.sleep(random.uniform(0.1, 0.5))
    
    async def bypass_vercel_security_checkpoint(self, url: str, page: Optional[AsyncPage] = None, 
                                     max_attempts: int = 3, timeout: int = 60000):
        """
        Cố gắng vượt qua điểm kiểm tra bảo mật của Vercel với thuật toán cải tiến
        
        Args:
            url: URL cần truy cập
            page: Trang để sử dụng, mặc định là self.page
            max_attempts: Số lần thử tối đa
            timeout: Thời gian chờ tối đa (ms)
            
        Returns:
            bool: True nếu bypass thành công
        """
        target_page = page if page else self.page
        
        # Thiết lập headers giống trình duyệt thật
        await target_page.set_extra_http_headers({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1"
        })
        
        # Thêm cookies để giả vờ đã truy cập trước đó
        await target_page.context.add_cookies([{
            'name': '_vercel_visited',
            'value': '1',
            'domain': urlparse(url).netloc,
            'path': '/'
        }])
        
        for attempt in range(max_attempts):
            try:
                # Truy cập URL với các tùy chọn thích hợp
                await target_page.goto(url, wait_until='networkidle', timeout=timeout)
                
                # Kiểm tra xem có điểm kiểm tra bảo mật không
                is_checkpoint = await target_page.evaluate('''
                    () => {
                        const selectors = [
                            "text=Security Check",
                            "text=Vercel Security",
                            "[data-testid='security-checkpoint']",
                            "form[action*='challenge']",
                            "[id*='challenge']"
                        ];
                        
                        for (const selector of selectors) {
                            try {
                                if (document.querySelector(selector)) {
                                    return true;
                                }
                            } catch(e) {}
                        }
                        
                        return document.body.textContent.includes("Security Check") || 
                            document.body.textContent.includes("Vercel Security");
                    }
                ''')
                
                if is_checkpoint:
                    print("Vercel security checkpoint detected, bypassing...")
                    
                    # 1. Mô phỏng hành vi người dùng trước khi tương tác
                    await self.simulate_human_behavior(target_page)
                    await self.perform_human_like_mouse_movements(target_page)
                    await asyncio.sleep(random.uniform(1.0, 2.5))
                    
                    # 2. Tìm và xử lý các yếu tố bảo mật
                    # Checkbox
                    if await self.element_exists("[type='checkbox']", page=target_page, timeout=5000):
                        checkbox = await target_page.query_selector("[type='checkbox']")
                        if checkbox:
                            box = await checkbox.bounding_box()
                            if box:
                                # Di chuyển chuột theo đường cong tự nhiên
                                start_x = box['x'] + box['width'] * random.uniform(1.5, 2.5)
                                start_y = box['y'] + box['height'] * random.uniform(1.5, 2.5)
                                
                                # Tạo điểm điều khiển cho đường cong Bezier
                                control_x = (start_x + box['x'] + box['width']/2) / 2 + random.uniform(-20, 20)
                                control_y = (start_y + box['y'] + box['height']/2) / 2 + random.uniform(-10, 10)
                                
                                # Di chuyển chuột theo đường cong
                                steps = 15
                                for i in range(steps + 1):
                                    t = i / steps
                                    # Đường cong bậc 2
                                    pos_x = pow(1-t, 2) * start_x + 2 * (1-t) * t * control_x + pow(t, 2) * (box['x'] + box['width']/2)
                                    pos_y = pow(1-t, 2) * start_y + 2 * (1-t) * t * control_y + pow(t, 2) * (box['y'] + box['height']/2)
                                    
                                    await target_page.mouse.move(pos_x, pos_y)
                                    await asyncio.sleep(random.uniform(0.01, 0.03))
                                
                                # Nhấp chuột với độ trễ
                                await target_page.mouse.click(
                                    box['x'] + box['width'] / 2, 
                                    box['y'] + box['height'] / 2,
                                    delay=random.uniform(50, 150)
                                )
                                await asyncio.sleep(random.uniform(0.5, 1.0))
                    
                    # 3. Tìm và nhấn các nút xác nhận
                    button_selectors = [
                        "text=Verify",
                        "text=Continue", 
                        "text=I'm not a robot",
                        "[type='submit']",
                        "button:visible",
                        "a.button",
                        "[role='button']",
                        "[aria-role='button']"
                    ]
                    
                    for selector in button_selectors:
                        if await self.element_exists(selector, page=target_page, timeout=2000):
                            # Di chuyển đến nút một cách tự nhiên trước khi click
                            button = await target_page.query_selector(selector)
                            if button:
                                await button.hover({force: true})
                                await asyncio.sleep(random.uniform(0.2, 0.5))
                                await button.click(delay=random.uniform(50, 120))
                                break
                    
                    # 4. Xử lý các trường input khác nếu có
                    input_selectors = ["input:not([type='checkbox'])", "textarea"]
                    for selector in input_selectors:
                        inputs = await target_page.query_selector_all(selector)
                        for input_elem in inputs:
                            # Chỉ điền nếu trường input được hiển thị
                            if await input_elem.is_visible():
                                await input_elem.click(force=True)
                                # Nhập ký tự giống người dùng
                                input_type = await input_elem.get_attribute('type') or ''
                                if input_type.lower() == 'email':
                                    await self.type(selector, "user@example.com", page=target_page, human_like=True)
                                else:
                                    await self.type(selector, "verification", page=target_page, human_like=True)
                    
                    # 5. Đợi quá trình xác minh hoàn tất
                    await asyncio.sleep(random.uniform(2.0, 3.5))
                    await target_page.wait_for_load_state('networkidle', timeout=timeout)
                    
                    # 6. Kiểm tra xem đã vượt qua chưa
                    is_still_checkpoint = await target_page.evaluate('''
                        () => {
                            const selectors = [
                                "text=Security Check",
                                "text=Vercel Security",
                                "[data-testid='security-checkpoint']",
                            ];
                            
                            for (const selector of selectors) {
                                try {
                                    if (document.querySelector(selector)) {
                                        return true;
                                    }
                                } catch(e) {}
                            }
                            
                            return document.body.textContent.includes("Security Check") || 
                                document.body.textContent.includes("Vercel Security");
                        }
                    ''')
                    
                    if not is_still_checkpoint:
                        print("Successfully bypassed Vercel security")
                        return True
                else:
                    # Không có điểm kiểm tra bảo mật
                    return True
            
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {str(e)}")
            
            # Chờ một lúc trước khi thử lại với cách tiếp cận khác
            await asyncio.sleep(random.uniform(1.5, 3.0))
        
        return False 
    
    async def auto_click_recapcha(self, reset_context: bool = False):
        """
        Tự động click vào nút "I'm not a robot" của Google reCAPTCHA và giải captcha
        
        Args:
            reset_context: Đặt True để tạo context mới, False để sử dụng context hiện tại
        """
        # Đóng context hiện tại nếu yêu cầu reset
        if reset_context and self.context:
            await self.context.close()
            self.context = None
        
        # Tạo browser context mới nếu cần
        if not self.context:
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                device_scale_factor=1.75,  # 1.75 giống hơn với màn hình thực tế
                has_touch=True,
                locale='en-US',
                color_scheme='light',
                reduced_motion='no-preference',
                forced_colors='none'
            )
            
            # Tạo page mới nếu cần
            if not self.page or not self.page.is_connected():
                self.page = await self.context.new_page()
        
        # Script nâng cao để tự động giải captcha
        await self.context.add_init_script("""
        () => {
            // 1. Đánh dấu reCAPTCHA đã được phát hiện
            let recaptchaDetected = false;
            let hcaptchaDetected = false;
            let turnstileDetected = false;
            
            // 2. Giám sát và xử lý reCAPTCHA 
            const recaptchaObserver = setInterval(() => {
                try {
                    // reCAPTCHA v2 Checkbox
                    const recaptchaCheckbox = document.querySelector('.recaptcha-checkbox-border:not([disabled])');
                    if (recaptchaCheckbox && !recaptchaCheckbox.closest('.recaptcha-checkbox-checked')) {
                        console.log('reCAPTCHA checkbox detected, clicking...');
                        recaptchaDetected = true;
                        
                        // Mô phỏng một loạt các sự kiện giống người dùng
                        const rect = recaptchaCheckbox.getBoundingClientRect();
                        const centerX = rect.left + rect.width / 2;
                        const centerY = rect.top + rect.height / 2;
                        
                        // Các sự kiện chuột hover
                        recaptchaCheckbox.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
                        recaptchaCheckbox.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));
                        
                        // Thêm độ trễ nhỏ
                        setTimeout(() => {
                            // Click với sự kiện đầy đủ
                            recaptchaCheckbox.dispatchEvent(new MouseEvent('mousedown', {
                                bubbles: true, clientX: centerX, clientY: centerY
                            }));
                            
                            setTimeout(() => {
                                recaptchaCheckbox.dispatchEvent(new MouseEvent('mouseup', {
                                    bubbles: true, clientX: centerX, clientY: centerY
                                }));
                                recaptchaCheckbox.dispatchEvent(new MouseEvent('click', {
                                    bubbles: true, clientX: centerX, clientY: centerY
                                }));
                            }, Math.random() * 50 + 10);
                        }, Math.random() * 100 + 50);
                    }
                    
                    // reCAPTCHA v3 (giải audio nếu có)
                    const audioButton = document.querySelector('.rc-button-audio');
                    if (audioButton && recaptchaDetected) {
                        console.log('reCAPTCHA audio button detected');
                        // Thực hiện click vào nút audio
                        setTimeout(() => {
                            audioButton.click();
                        }, Math.random() * 1000 + 500);
                    }
                    
                    // hCaptcha
                    const hcaptchaCheckbox = document.querySelector('.h-captcha iframe, #h-captcha iframe');
                    if (hcaptchaCheckbox) {
                        console.log('hCaptcha detected');
                        hcaptchaDetected = true;
                        
                        // Tìm iframe và switch focus vào iframe đó
                        const iframeSrc = hcaptchaCheckbox.src || '';
                        if (iframeSrc && !hcaptchaCheckbox.dataset.clicked) {
                            hcaptchaCheckbox.dataset.clicked = 'true';
                            setTimeout(() => {
                                try {
                                    hcaptchaCheckbox.contentWindow.document.querySelector('.checkbox').click();
                                } catch (e) {
                                    console.log('Unable to click inside hCaptcha iframe due to same-origin policy');
                                    // Fall back để click trực tiếp vào iframe
                                    hcaptchaCheckbox.click();
                                }
                            }, Math.random() * 800 + 200);
                        }
                    }
                    
                    // Cloudflare Turnstile
                    const turnstileFrame = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
                    if (turnstileFrame) {
                        console.log('Turnstile detected');
                        turnstileDetected = true;
                        
                        // Thử click vào các checkbox trong iframe
                        setTimeout(() => {
                            try {
                                const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                                checkboxes.forEach(checkbox => {
                                    if (!checkbox.checked) checkbox.click();
                                });
                            } catch (e) {
                                console.log('Turnstile interaction error', e);
                            }
                        }, Math.random() * 1000 + 300);
                    }
                    
                    // Xử lý captcha image challenges
                    if (recaptchaDetected || hcaptchaDetected) {
                        // Tìm kiếm các hình ảnh trong captcha challenge
                        const captchaImages = document.querySelectorAll('.rc-imageselect-tile img, .task-image img');
                        if (captchaImages.length > 0) {
                            console.log('Captcha image challenge detected');
                        }
                    }
                    
                } catch(e) {
                    console.log('Captcha monitoring error:', e);
                }
            }, 1000);
            
            // 3. Giám sát các hành vi reCAPTCHA 
            const captchaFrameObserver = new MutationObserver((mutations) => {
                for (const mutation of mutations) {
                    if (mutation.addedNodes.length > 0) {
                        for (const node of mutation.addedNodes) {
                            if (node.nodeName === 'IFRAME') {
                                const src = node.src || '';
                                if (src.includes('recaptcha') || src.includes('hcaptcha') || src.includes('turnstile')) {
                                    console.log('New captcha iframe detected:', src);
                                    // Tạo focus vào iframe
                                    setTimeout(() => node.focus(), 500);
                                }
                            }
                        }
                    }
                }
            });
            
            // Bắt đầu quan sát DOM
            captchaFrameObserver.observe(document.body, { childList: true, subtree: true });
        }
        """)
        
        return self.context

    async def bypass_cloudflare(self, url: str, page: Optional[AsyncPage] = None, timeout: int = 90000):
        """
        Bypass Cloudflare Flow Challenge mới nhất (ov1) - phiên bản đầy đủ 2025
        
        Args:
            url: URL chứa challenge
            page: Trang để sử dụng, mặc định là self.page
            timeout: Thời gian chờ tối đa (ms)
        
        Returns:
            bool: True nếu bypass thành công, False nếu không
        """
        
        target_page = page if page else self.page

        # 2. Thiết lập User-Agent và headers giống Chrome thật
        await target_page.set_extra_http_headers({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-User": "?1",
            "Priority": "high"
        })
        
        # 3. Thêm script siêu cao cấp để xử lý Cloudflare Flow Challenge 2025
        await target_page.add_init_script("""
        () => {
            // ---------- TIẾP CẬN 1: NGỤ TRANG HOÀN TOÀN NAVIGATOR ----------
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'plugins', { 
                get: () => {
                    const plugins = [
                        {
                            0: {type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format'},
                            name: 'PDF Viewer',
                            description: 'Portable Document Format',
                            filename: 'internal-pdf-viewer'
                        },
                        {
                            0: {type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format'},
                            name: 'Chrome PDF Viewer',
                            description: 'Portable Document Format',
                            filename: 'internal-pdf-viewer'
                        },
                        {
                            0: {type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format'},
                            name: 'Chromium PDF Viewer',
                            description: 'Portable Document Format',
                            filename: 'internal-pdf-viewer'
                        },
                        {
                            0: {type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format'},
                            name: 'Microsoft Edge PDF Viewer',
                            description: 'Portable Document Format',
                            filename: 'internal-pdf-viewer'
                        },
                        {
                            0: {type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format'},
                            name: 'WebKit built-in PDF',
                            description: 'Portable Document Format',
                            filename: 'internal-pdf-viewer'
                        },
                        {
                            0: {type: 'application/x-google-chrome-pdf', suffixes: 'pdf', description: 'Portable Document Format'},
                            name: 'Chrome PDF Plugin',
                            description: 'Portable Document Format',
                            filename: 'internal-pdf-viewer'
                        },
                        {
                            0: {type: 'application/x-shockwave-flash', suffixes: 'swf', description: 'Shockwave Flash'},
                            name: 'Shockwave Flash',
                            description: 'Shockwave Flash 32.0 r0',
                            filename: 'pepflashplayer.dll'
                        }
                    ];
                    
                    // Tạo object đúng prototype
                    plugins.__proto__ = PluginArray.prototype;
                    plugins.length = plugins.length;
                    plugins.refresh = function() {};
                    
                    // Thêm phương thức named item và item
                    plugins.namedItem = function(name) {
                        return plugins.find(p => p.name === name);
                    };
                    
                    plugins.item = function(index) {
                        return plugins[index];
                    };
                    
                    return plugins;
                }
            });

            // ---------- TIẾP CẬN 2: HARDWARE CONCURRENCY & DEVICE MEMORY ----------
            
            // Thiết lập giá trị chân thực cho hardware concurrency (4-16)
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => Math.floor(Math.random() * 12) + 4
            });
            
            // Thiết lập giá trị thiết bị thực cho device memory (2-8GB) 
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => Math.pow(2, Math.floor(Math.random() * 3) + 1)
            });
            
            // ---------- TIẾP CẬN 3: BROWSER HISTORY & PERFORMANCE ----------
            
            // Mô phỏng lịch sử duyệt web (thêm entries giả vào history)
            const createFakeHistoryEntry = () => {
                const popStateEvent = new PopStateEvent('popstate', {
                    bubbles: false,
                    cancelable: false,
                    state: Math.random().toString(36).substring(2)
                });
                window.dispatchEvent(popStateEvent);
                
                // Thêm một entry vào history API để giống người dùng thực đã lướt web
                window.history.pushState(
                    {random: Math.random()},
                    '',
                    window.location.href
                );
            };
            
            // Tạo vài entries ngẫu nhiên (1-3 entries)
            const numEntries = Math.floor(Math.random() * 3) + 1;
            for (let i = 0; i < numEntries; i++) {
                setTimeout(createFakeHistoryEntry, Math.random() * 1000);
            }
            
            // ---------- TIẾP CẬN 4: CANVAS & WEBGL FINGERPRINTING ----------
            
            // Override Canvas method để thêm nhiễu nhỏ vào fingerprinting
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type, quality) {
                // Kiểm tra nếu đang có hành vi fingerprinting canvas
                if (type === 'image/png' && this.width === 16 && this.height === 16) {
                    // Canvas đang được dùng để fingerprint
                    
                    // Thực hiện phương thức gốc, nhưng thêm nhiễu nhỏ
                    const data = originalToDataURL.apply(this, arguments);
                    
                    // Thêm nhiễu ngẫu nhiên không đáng kể vào dữ liệu
                    const noise = Math.floor(Math.random() * 10000).toString(16).padStart(4, '0');
                    const modifiedData = data.substring(0, data.length - 10) + noise + data.substring(data.length - 6);
                    
                    return modifiedData;
                }
                
                // Không phải fingerprinting, trả về kết quả bình thường
                return originalToDataURL.apply(this, arguments);
            };
            
            // Override getImageData để thêm nhiễu không đáng kể
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            CanvasRenderingContext2D.prototype.getImageData = function() {
                const imageData = originalGetImageData.apply(this, arguments);
                
                // Chỉ thêm nhiễu với xác suất 20% để tránh ảnh hưởng giao diện
                if (Math.random() < 0.2) {
                    // Thêm nhiễu pixel không đáng kể
                    const length = imageData.data.length;
                    
                    // Chỉ chỉnh sửa vài pixel (không đáng kể)
                    const numPixelsToModify = Math.min(5, length / 4);
                    
                    for (let i = 0; i < numPixelsToModify; i++) {
                        const pixelIndex = Math.floor(Math.random() * (length / 4)) * 4;
                        const smallNoise = Math.floor(Math.random() * 3) - 1; // -1, 0, or 1
                        
                        // Thêm nhiễu cực nhỏ vào giá trị R, G, hoặc B
                        const channelToModify = Math.floor(Math.random() * 3);
                        imageData.data[pixelIndex + channelToModify] = 
                            Math.max(0, Math.min(255, imageData.data[pixelIndex + channelToModify] + smallNoise));
                    }
                }
                
                return imageData;
            };
            
            // WebGL fingerprinting protection
            const getParameterProxied = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // UNMASKED_VENDOR_WEBGL
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                // UNMASKED_RENDERER_WEBGL
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameterProxied.apply(this, arguments);
            };
            
            // ---------- TIẾP CẬN 5: TRUY CẬP MEMORY & CPU ----------
            
            // Giả mạo các giá trị hiệu năng không đồng nhất để tránh phát hiện
            const originalNow = performance.now;
            let lastTime = 0;
            performance.now = function() {
                const precise = originalNow.call(performance);
                if (lastTime === 0) {
                    lastTime = precise;
                    return precise;
                }
                
                // Tăng thời gian một chút (lên đến 3ms) để tạo sự không đồng nhất
                const max_increment = 3;
                const increment = Math.random() * max_increment;
                lastTime = Math.max(lastTime + increment, precise);
                return lastTime;
            };
            
            // ---------- TIẾP CẬN 6: SESSION & COOKIES ----------
            
            // Thêm cookie người dùng thực
            const addRandomCookie = () => {
                const cookieName = 'browser_session_' + Math.random().toString(36).substring(2);
                const cookieValue = Math.random().toString(36) + Math.random().toString(36);
                document.cookie = `${cookieName}=${cookieValue}; path=/; max-age=${60*60*24*7}`;
            };
            
            // Thêm cookie ngẫu nhiên
            if (Math.random() > 0.3) {
                addRandomCookie();
            }
            
            // ---------- TIẾP CẬN 7: XỬ LÝ CẢNH BÁO CLOUDFLARE ----------
            
            // Xử lý các thẻ cảnh báo của Cloudflare
            const handleCloudflareElements = () => {
                const elements = document.querySelectorAll('#challenge-running, #challenge-spinner, #challenge-error');
                elements.forEach(el => {
                    if (el) {
                        // Làm cho element mờ đi
                        el.style.opacity = '0.6';
                    }
                });
                
                // Thử click vào nút submit/verify nếu có
                const verifyButtons = document.querySelectorAll('input[type="submit"], button[type="submit"], .rc-button-default');
                verifyButtons.forEach(btn => {
                    if (btn && btn.offsetParent !== null) {
                        setTimeout(() => {
                            btn.click();
                        }, Math.random() * 1000 + 500);
                    }
                });
            };
            
            setInterval(handleCloudflareElements, 1000);
            
            // ---------- TIẾP CẬN 8: CHỐNG PHÁT HIỆN TỰ ĐỘNG TRÌNH DUYỆT ----------
            
            // Cloudflare có thể kiểm tra các đặc điểm Chrome automation
            if (window.chrome) {
                // Thêm thuộc tính extension
                window.chrome.runtime = window.chrome.runtime || {};
                
                // Thêm các thuộc tính app
                window.chrome.app = {
                    isInstalled: false,
                    getDetails: function() { return null; },
                    getIsInstalled: function() { return false; },
                    runningState: function() { return 'cannot_run'; }
                };
                
                // Thêm csp thuộc tính
                window.chrome.csi = function() { 
                    return {
                        onloadT: Date.now(),
                        startE: Date.now(),
                        pageT: Date.now() - (Math.floor(Math.random() * 1000) + 100),
                        tran: 15
                    }; 
                };
            }
            
            // ---------- TIẾP CẬN 9: THÊM GIÁM SÁT TURNSTILE ----------
            
            // Kiểm tra và xử lý Cloudflare Turnstile
            setInterval(() => {
                // Tìm Cloudflare Turnstile frame
                const frames = document.querySelectorAll('iframe[src*="challenges.cloudflare.com"], iframe[src*="turnstile"]');
                frames.forEach(frame => {
                    try {
                        // Thử click checkbox
                        const frameDocument = frame.contentDocument || frame.contentWindow.document;
                        const checkbox = frameDocument.querySelector('input[type="checkbox"]');
                        if (checkbox && !checkbox.checked) {
                            checkbox.click();
                        }
                    } catch (e) {
                        // Bỏ qua lỗi CORS
                    }
                });
                
                // Kiểm tra nút xác nhận
                const verifyButtons = document.querySelectorAll('[data-testid="challenge-submit"], [data-action="submit"]');
                verifyButtons.forEach(btn => {
                    if (btn) {
                        btn.click(force=True);
                    }
                });
            }, 2000);
            
            // ---------- TIẾP CẬN 10: ĐÁNH LỪA CF-BROWSER-CHECKS ----------
            
            // Cloudflare kiểm tra cửa sổ
            Object.defineProperty(window, 'innerWidth', {
                get: function() { 
                    return 1366 + Math.floor(Math.random() * 100); 
                }
            });
            
            // Chặn cookie-checking
            const originalDocCookie = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie');
            Object.defineProperty(Document.prototype, 'cookie', {
                get: function() {
                    return originalDocCookie.get.call(this);
                },
                set: function(val) {
                    // Thêm cookie ngẫu nhiên nếu đang set cookie Cloudflare
                    if (val.includes('cf_') || val.includes('_cf') || val.includes('__cf')) {
                        // Thêm noise vào Cloudflare cookies
                        const noiseCookie = 'cf_clearance_aux=' + Math.random().toString(36).substring(2);
                        originalDocCookie.set.call(this, noiseCookie);
                    }
                    return originalDocCookie.set.call(this, val);
                }
            });
        }
        """)
        
        try:
            # 4. Thiết lập giám sát network cho các request đặc biệt
            async def handle_route(route):
                request = route.request
                url = request.url
                
                if 'cloudflare' in url or 'cdn-cgi' in url or 'challenges' in url:
                    headers = {
                        **request.headers,
                        'Sec-Ch-Ua-Platform': '"Windows"',
                        'Accept': 'application/json, text/plain, */*',
                        'Cf-Challenge': 'bd7dab2219e01c6b8669724b9abe7dd5'
                    }
                    await route.continue_(headers=headers)
                else:
                    await route.continue_()
            
            await target_page.route('**/*', handle_route)
            # Khởi tạo các biến theo dõi
            challenge_detected = False
            solve_attempts = 0
            start_time = time.time() * 1000  # Thời gian hiện tại tính bằng ms
            
            # Truy cập URL
            await target_page.goto(url, timeout = int(timeout / 2), waitUntil = 'domcontentloaded', referer = 'https://www.google.com/' )
            
            # 6. Xử lý challenge
            while (time.time() * 1000 - start_time) < timeout:
                # Kiểm tra các dấu hiệu của Flow Challenge
                is_challenge = await target_page.evaluate("""
                    () => {
                        return !!(
                            document.querySelector('iframe[src*="flow"]') ||
                            document.querySelector('iframe[src*="challenges.cloudflare.com"]') ||
                            document.querySelector('#challenge-running') ||
                            document.querySelector('#challenge-spinner') ||
                            document.querySelector('#challenge-body-text') ||
                            document.querySelector('#cf-challenge-running') ||
                            document.querySelector('.cf-browser-verification') ||
                            document.body.textContent.includes('Checking if the site connection is secure') ||
                            window.location.href.includes('/cdn-cgi/challenge-platform/')
                        );
                    }
                """)
                
                if not is_challenge:
                    return True
                
                # Bắt đầu giải challenge
                challenge_detected = True
                solve_attempts += 1
                
                # Mô phỏng hành vi người dùng
                await self.perform_human_like_mouse_movements(target_page)
                await self.simulate_human_behavior(target_page)
                
                # Xử lý các phần tử challenge (đã tách thành phương thức riêng)
                await self.handle_cloudflare_elements(target_page)
                
                # Phương pháp 3: Cải thiện cookie và cấp phát bộ nhớ
                if solve_attempts % 2 == 0:
                    # Thêm cookie ngẫu nhiên
                    await target_page.evaluate("""
                        () => {
                            const tokens = [
                                Math.random().toString(36).substring(2),
                                Math.random().toString(36).substring(2),
                                Math.random().toString(36).substring(2)
                            ];
                            
                            // Thêm "cf_clearance" giả
                            const clearanceValue = tokens.join('.') + '.' + Math.floor(Date.now()/1000);
                            document.cookie = `cf_clearance_custom=${clearanceValue}; path=/; max-age=86400`;
                            
                            // Xóa localStorage để tránh conflict
                            try {
                                localStorage.removeItem('cf_challenge');
                                localStorage.removeItem('cf_chl_rc_ni');
                            } catch(e) {}
                            
                            // Cấp phát bộ nhớ để tránh phát hiện low-memory automation
                            const mem = new Array(10000).fill('x').map(() => new Array(1000).fill('x'));
                            window._memoryAllocation = mem;
                            
                            // Tạo thuộc tính userActivity để giả lập người dùng thật
                            if (!window._userActivity) {
                                window._userActivity = {
                                    mouseMovements: Math.floor(Math.random() * 50) + 20,
                                    clicks: Math.floor(Math.random() * 10) + 2,
                                    keyPresses: Math.floor(Math.random() * 20),
                                    scrolls: Math.floor(Math.random() * 5) + 1,
                                    timeOnPage: Date.now() - (Math.floor(Math.random() * 30000) + 5000)
                                };
                            }
                        }
                    """)
                
                # Phương pháp 4: Tạo ảo giác scroll và hiệu ứng động
                if solve_attempts >= 2:
                    # Tạo một số hành vi để kích hoạt event listeners
                    scroll_amount = random.randint(50, 200)
                    for _ in range(3):
                        await target_page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                        await asyncio.sleep(random.uniform(0.2, 0.5))
                        await target_page.evaluate(f"window.scrollBy(0, -{scroll_amount})")
                        await asyncio.sleep(random.uniform(0.2, 0.5))
                
                # Phương pháp 5: Tải lại trang với giả định khác nếu thất bại nhiều lần
                if solve_attempts >= 3:
                    # Reload trang với staggering
                    await asyncio.sleep(random.uniform(1.5, 3.0))
                    await target_page.reload(wait_until='domcontentloaded')
                    solve_attempts = 0
                    
                    # Đợi một khoảng thời gian ngẫu nhiên sau khi tải lại
                    await asyncio.sleep(random.uniform(2.0, 4.0))
            
            # Nếu sau khi hết timeout mà vẫn đang ở challenge
            if challenge_detected:
                return False
            
            return True
        except Exception as e:
            return False
        
    async def handle_cloudflare_elements(self, page: Optional[AsyncPage] = None):
        """
        Xử lý và tương tác với các phần tử Cloudflare Challenge
        
        Args:
            page: Trang để xử lý, mặc định là self.page
        """
        target_page = page if page else self.page
        
        try:
            # 1. Tìm và xử lý iframe turnstile
            turnstile_frames = await target_page.query_selector_all('iframe[src*="challenges.cloudflare.com"], iframe[src*="turnstile"]')
            
            for frame in turnstile_frames:
                try:
                    frame_element = await frame.content_frame()
                    if frame_element:
                        # Check và click vào checkbox
                        checkbox = await frame_element.query_selector('input[type="checkbox"]')
                        if checkbox:
                            await checkbox.click(force=True)
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                        
                        # Click vào nút verify nếu có
                        verify_btn = await frame_element.query_selector('button[type="submit"], [data-action="submit"]')
                        if verify_btn:
                            await verify_btn.click(force=True)
                            await asyncio.sleep(random.uniform(1.0, 2.0))
                except Exception:
                    # Xử lý trực tiếp frame nếu không thể content_frame do CORS
                    box = await frame.bounding_box()
                    if box:
                        # Click vào giữa iframe
                        await target_page.mouse.click(
                            box['x'] + box['width'] / 2,
                            box['y'] + box['height'] / 2
                        )
                        await asyncio.sleep(random.uniform(0.5, 1.0))
            
            # 2. Xử lý các button và input
            elements_to_check = [
                '[type="checkbox"]:visible',
                'button[type="submit"]:visible', 
                '[data-testid="challenge-submit"]:visible',
                '[data-action="submit"]:visible',
                '#challenge-stage a:visible',
                '.challenge-button:visible',
                '[aria-label*="verify"]:visible'
            ]
            
            for selector in elements_to_check:
                try:
                    elements = await target_page.query_selector_all(selector)
                    for element in elements:
                        is_visible = await element.is_visible()
                        if is_visible:
                            # Thực hiện click với hover trước để tự nhiên hơn
                            await element.hover()
                            await asyncio.sleep(random.uniform(0.2, 0.7))
                            await element.click(delay=random.uniform(30, 150))
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                except Exception:
                    pass
            
            # 3. Thực thi script đặc biệt để xử lý automation checks
            await target_page.evaluate("""
                () => {
                    // Xóa bỏ các script theo dõi automation
                    const scriptsToClear = ['cf_chl_', '_cf_chl', 'cf-please-wait', 'cf_challenge'];
                    
                    for (const id of document.scripts) {
                        for (const keyword of scriptsToClear) {
                            if (id.src && id.src.includes(keyword)) {
                                id.dataset.handled = 'true'; // Đánh dấu đã xử lý
                            }
                        }
                    }
                    
                    // Thử upload cfc cookie
                    try {
                        const timestamp = Math.floor(Date.now() / 1000);
                        const token = btoa(Math.random().toString(36).substring(2));
                        document.cookie = `cfc_token=${token}.${timestamp}; path=/; max-age=86400`;
                    } catch (e) {}
                    
                    // Auto submit form nếu có
                    try {
                        const forms = document.querySelectorAll('form[action*="challenge"]');
                        for (const form of forms) {
                            if (!form.dataset.submitted) {
                                form.dataset.submitted = 'true';
                                setTimeout(() => form.submit(), Math.random() * 500 + 500);
                            }
                        }
                    } catch (e) {}
                }
            """)

        except Exception as e:
            print(f"Lỗi khi xử lý phần tử Cloudflare: {str(e)}")
        