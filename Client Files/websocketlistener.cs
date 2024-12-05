using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;
using System.Text;
using System.Net.WebSockets;
using UnityEngine;
using UnityEditor.Compilation;


public class websocketlistener : MonoBehaviour
{
    /// <summary>
    /// Semaphore code and docs
    /// solution >  https://stackoverflow.com/a/21163280
    /// SemaphoreSlim class > https://learn.microsoft.com/en-us/dotnet/api/system.threading.semaphoreslim?view=net-8.0
    /// 
    /// </summary>
    private static SemaphoreSlim semaphore = new SemaphoreSlim(1);

    /// <summary>
    /// websockets docs
    /// websocket support > https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/websockets
    /// ClientWebSocket class > https://learn.microsoft.com/en-us/dotnet/api/system.net.websockets.clientwebsocket?view=net-9.0
    /// </summary>
    Uri uri = new Uri("ws://localhost:8765");
    ClientWebSocket ws = new ClientWebSocket();
    byte[] buffer = new byte[1024];


    string JsonString;

    async void Start()
    {
        
        await ws.ConnectAsync(uri, default);

    }
    void FixedUpdate()
    {
        ReceiveData();
    }

    private void OnApplicationQuit()
    {
        CloseSocket();
    }

    async void ReceiveData()
    {
        // semaphore timeout is set to 0
        // prevents receive requests from backing up
        if (await semaphore.WaitAsync(0))
        {
            try
            {
                var result = await ws.ReceiveAsync(buffer, default);

                JsonString = Encoding.UTF8.GetString(buffer, 0, result.Count);
                Debug.Log(JsonString);
            }
            finally
            {
                semaphore.Release();
            }
        }
        
    }

    async void CloseSocket()
    {
        await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "Client closed", default);
    }

}