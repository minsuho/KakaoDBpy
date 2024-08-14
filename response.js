// 개선된 TCP 소켓 서버 코드

var threadPool = java.util.concurrent.Executors.newFixedThreadPool(10);  // 스레드 풀 생성
var listener;  // 전역 listener 변수

var thread1 = new java.lang.Thread({
    run: function() {
        try {
            listener = new java.net.ServerSocket(3000);
            while (true) {
                try {
                    var _socket = listener.accept();
                    threadPool.submit(new java.lang.Runnable({
                        run: function() {
                            SocketHandler(_socket);
                        }
                    }));
                } catch (e) {
                    if (!listener.isClosed()) {
                        Log.e("Error accepting connection: " + e.message);
                    }
                }
            }
        } catch (e) {
            Log.e("Error creating ServerSocket: " + e.message);
        } finally {
            closeListener();
        }
    }
});
thread1.start();

function onStartCompile() {
    closeListener();
}

function closeListener() {
    try {
        if (listener && !listener.isClosed()) {
            listener.close();
        }
    } catch (e) {
        Log.e("Error closing listener: " + e.message);
    }
}

function SocketHandler(socket) {
    var ins = null;
    var br = null;

    try {
        ins = socket.getInputStream();
        br = new java.io.BufferedReader(new java.io.InputStreamReader(ins));
        var line = "";
        while ((line = br.readLine()) != null) {
            if (line.trim() === "")
                break;
            if (line.startsWith("{")) {
                replyResult(line);
            }
        }
    } catch (e) {
        Log.e("Error in SocketHandler: " + e.message);
    } finally {
        closeResources(br, ins, socket);
    }
}

function closeResources(br, ins, socket) {
    try {
        if (br) br.close();
        if (ins) ins.close();
        if (socket) socket.close();
    } catch (e) {
        Log.e("Error closing resources: " + e.message);
    }
}

function base64Decode(input) {
    try {
        let decoder = java.util.Base64.getDecoder();
        let decodedByteArray = decoder.decode(input);
        return new java.lang.String(decodedByteArray, "UTF-8") + "";
    } catch (e) {
        Log.e("Error in base64Decode: " + e.message);
        return null;
    }
}

function replyResult(data) {
    try {
        data = JSON.parse(data);
        data.data = base64Decode(data.data);
        data.room = base64Decode(data.room);
        data.roomId = data.roomId ? BigInt(data.roomId) : null;

        if (data.isSuccess) {
            if (data.roomId) {
                Api.replyRoom(data.roomId, data.data);
            } else if (data.room) {
                Api.replyRoom(data.room,data.data);
            }
        }
    } catch (e) {
        Log.e("Error in replyResult: " + e.message);
    }
}
