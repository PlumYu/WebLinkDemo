# sse_app/views.py
import time
import json
from django.http import StreamingHttpResponse
import sys # For flushing stdout during debug

def sse_stream(request):
    print(f"[{time.strftime('%H:%M:%S')}] SSE connection request received.")
    sys.stdout.flush() # 确保日志立即显示

    def event_stream():
        print(f"[{time.strftime('%H:%M:%S')}] event_stream generator started.")
        sys.stdout.flush()
        
        count = 0
        client_connected = True # Assume connected initially

        try:
            # 发送第一个事件，确保 onopen 能触发
            count += 1
            current_timestamp_seconds = int(time.time())
            payload = {
                "id": count,
                "message": f"Initial Event: Server time {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "timestamp": current_timestamp_seconds
            }
            message_data_json = json.dumps(payload)
            
            # SSE 事件格式：
            # event: <event_name> (optional, defaults to 'message')
            # id: <event_id> (optional)
            # data: <event_data>
            # retry: <milliseconds> (optional)
            # Multiple data lines are allowed for a single event.
            # An event is terminated by a blank line (\n\n).

            initial_event_lines = [
                f"id: {count}",
                f"event: message", # Explicitly set event type
                f"data: {message_data_json}"
            ]
            initial_event = "\n".join(initial_event_lines) + "\n\n" # Crucial: ends with \n\n

            print(f"[{time.strftime('%H:%M:%S')}] Preparing to yield INITIAL event (ID: {count}): {message_data_json}")
            sys.stdout.flush()
            yield initial_event.encode('utf-8')
            print(f"[{time.strftime('%H:%M:%S')}] Yielded INITIAL event (ID: {count}).")
            sys.stdout.flush()

            # 现在可以进入循环发送后续事件
            while count < 1000:
                count += 1
                current_timestamp_seconds = int(time.time())
                payload = {
                    "id": count,
                    "message": f"Update: Server time {time.strftime('%Y-%m-%d %H:%M:%S')}",
                    "timestamp": current_timestamp_seconds
                }
                message_data_json = json.dumps(payload)
                
                event_lines = [
                    f"id: {count}",
                    f"event: message",
                    f"data: {message_data_json}"
                ]
                sse_event = "\n".join(event_lines) + "\n\n"

                print(f"[{time.strftime('%H:%M:%S')}] Preparing to yield event (ID: {count}): {message_data_json}")
                sys.stdout.flush()
                yield sse_event.encode('utf-8')
                print(f"[{time.strftime('%H:%M:%S')}] Yielded event (ID: {count}).")
                sys.stdout.flush()

                # 在真实应用中，这里可以检查客户端是否仍然连接
                # 对于 StreamingHttpResponse 和同步生成器，GeneratorExit 是主要的断开连接信号

        except GeneratorExit:
            # 这个异常会在客户端断开连接时由 StreamingHttpResponse 注入到生成器中
            print(f"[{time.strftime('%H:%M:%S')}] SSE client disconnected (GeneratorExit in event_stream).")
            client_connected = False # 确保循环会终止 (虽然异常已经跳出循环)
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] SSE event_stream error: {e}")
            # 在生产中，你可能想向客户端发送一个错误事件，但这比较复杂
        finally:
            print(f"[{time.strftime('%H:%M:%S')}] event_stream generator finished (ID: {count}).")
            sys.stdout.flush()

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    # 这些头部对于 SSE 和防止代理缓冲非常重要
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache' # For HTTP/1.0 proxies
    response['Expires'] = '0' # For HTTP/1.0 proxies
    response['Connection'] = 'keep-alive'
    response['X-Accel-Buffering'] = 'no' # Crucial for Nginx and similar proxies

    print(f"[{time.strftime('%H:%M:%S')}] StreamingHttpResponse created, returning response.")
    sys.stdout.flush()
    return response