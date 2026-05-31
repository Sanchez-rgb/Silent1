
# 测试脚本 - 输出到文件
import sys

log_file = open('test_log.txt', 'w', encoding='utf-8')

def log(msg):
    print(msg)
    log_file.write(msg + '\n')
    log_file.flush()

log("开始测试...")
log("Python: " + sys.version)

try:
    log("\n1. 导入FastAPI...")
    import fastapi
    log("OK")
except Exception as e:
    log("ERROR: " + str(e))
    import traceback
    log(traceback.format_exc())
    log_file.close()
    sys.exit(1)

try:
    log("\n2. 添加路径...")
    sys.path.insert(0, 'c:\\Users\\55382\\Documents\\trae_projects\\j')
    log("OK")
except Exception as e:
    log("ERROR: " + str(e))
    log_file.close()
    sys.exit(1)

try:
    log("\n3. 导入main_v2...")
    import main_v2
    log("OK")
    log("App: " + str(main_v2.app))
except Exception as e:
    log("ERROR: " + str(e))
    import traceback
    log(traceback.format_exc())
    log_file.close()
    sys.exit(1)

try:
    log("\n4. 测试路由...")
    log("Routes: " + str(len(main_v2.app.routes)))
    for r in main_v2.app.routes:
        log("  " + str(r.path) + " " + str(r.methods))
    log("OK")
except Exception as e:
    log("ERROR: " + str(e))
    import traceback
    log(traceback.format_exc())
    log_file.close()
    sys.exit(1)

try:
    log("\n5. 测试客户端...")
    from fastapi.testclient import TestClient
    client = TestClient(main_v2.app)
    
    log("  测试/...")
    r = client.get("/")
    log("    Status: " + str(r.status_code))
    log("    Response: " + str(r.text))
    
    log("  测试/health...")
    r = client.get("/health")
    log("    Status: " + str(r.status_code))
    log("    Response: " + str(r.text))
    
    log("OK")
except Exception as e:
    log("ERROR: " + str(e))
    import traceback
    log(traceback.format_exc())
    log_file.close()
    sys.exit(1)

log("\n测试完成，全部通过！")
log_file.close()
