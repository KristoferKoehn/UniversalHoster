using Godot;
using Microsoft.VisualBasic;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Sockets;
using System.Text.Json;
using System.Xml.Linq;

public class UniversalConnector
{
    private string HostUUID;
    private string UniversalHosterIP;
    private int Port;


    static byte[] JsonToUtf8Bytes(object data)
    {
        try
        {
            // Serialize the object to a UTF-8 encoded byte array
            return JsonSerializer.SerializeToUtf8Bytes(data);
        }
        catch (Exception e)
        {
            Console.WriteLine($"Error converting JSON to UTF-8: {e.Message}");
            return null;
        }
    }

    static JsonElement Utf8StringToJson(string utf8JsonString)
    {
        try
        {
            // Parse the UTF-8 encoded JSON string into a JsonDocument
            JsonDocument jsonDocument = JsonDocument.Parse(utf8JsonString);

            // Access the root element of the JsonDocument
            return jsonDocument.RootElement;
        }
        catch (Exception e)
        {
            Console.WriteLine($"Error converting UTF-8 to JSON: {e.Message}");
            return default;
        }
    }


    /// <summary>
    /// Initializes the Universal Hoster IP address. The Universal Hoster must be online and configured correctly for this class to work.
    /// </summary>
    /// <param name="IpAddress"></param>
    public UniversalConnector(string IpAddress, int Port)
    {
        UniversalHosterIP = IpAddress;
        this.Port = Port;
    }

    /// <summary>
    /// returns a list of all servers currently hosted, the format is UUID, a space, then the server name.
    /// Here are some examples of the format:
    /// c4f05e26-236a-44e5-bdc5-1611b54df8e7 test
    /// 33932e52-4757-478e-b61c-f177e0a07217 server name can have any character #!?||
    /// </summary>
    /// <returns></returns>
    public List<string> Browse()
    {
        string response = SendCommand("{\"request_type\": \"browse\",\"data\":{}}");
        GD.Print(response);
        JsonElement dict = Utf8StringToJson(response);
        List<string> result = new List<string>();
        if (dict.TryGetProperty("data", out JsonElement dataElement))
        {
            if (dataElement.TryGetProperty("servers", out JsonElement serversElement) && serversElement.ValueKind == JsonValueKind.Array)
            {
                // Access values in the JSON array using EnumerateArray
                foreach (JsonElement item in serversElement.EnumerateArray())
                {
                    result.Add($"{item.GetProperty("uuid")} {item.GetProperty("server_name")}");
                }
            }
        }
        else
        {
            Console.WriteLine("Failed to convert UTF-8 to JSON or key3 is not an array.");
        }
    
        return result;
    }

    /// <summary>
    /// Joins server with given UUID. UUID can be obtained with data returned from Browse
    /// </summary>
    /// <param name="UUID"></param>
    /// <returns></returns>
    public string Join(string UUID)
    {
        string msg = SendCommand($"{{\"request_type\": \"join\",\"data\": {{\"unique_identifier\": \"{UUID}\"}}}}");
        JsonElement jso = Utf8StringToJson(msg);
        return jso.GetProperty("data").GetProperty("ip").ToString();
    }

    private string SendCommand(string command)
    {
        TcpClient client = new TcpClient(UniversalHosterIP, Port);
        NetworkStream stream = client.GetStream();
        StreamReader reader = new StreamReader(stream);
        StreamWriter writer = new StreamWriter(stream);

        writer.WriteLine(command);
        writer.Flush();

        string response = reader.ReadToEnd();
        return response;
    }

    /// <summary>
    /// Submits IP of local machine and the given server name to UniversalHoster server. The server name will be viewable by other players. This changes internal state to hold 
    /// the returned HostUUID. 
    /// </summary>
    /// <param name="ServerName"></param>
    /// <returns></returns>
    public string Host(string ServerName, string ip_address) { 
        return SendCommand($"{{\"request_type\": \"host\", \"data\": {{\"ip_address\":\"{ip_address}\",\"server_name\":\"{ServerName}\"}}}}");
    }

    /// <summary>
    /// Deletes the given UUID's host listing on the server. Be sure to only allow a user to end their own host. 
    /// </summary>
    /// <param name="UUID"></param>
    /// <returns></returns>
    public bool EndHost(string UUID)
    {
        return SendCommand($"delete {UUID}").Count() > 0;
    }

}
