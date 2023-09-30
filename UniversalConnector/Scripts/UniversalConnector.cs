using Godot;
using Microsoft.VisualBasic;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Sockets;
using System.Xml.Linq;

public class UniversalConnector
{
    private string HostUUID;
    private string UniversalHosterIP;
    private int Port;

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
        string response = SendCommand("browse");
        string[] strings = response.Split('\n');
        List<string> result = strings.ToList<string>();
        return result;
    }

    /// <summary>
    /// Joins server with given UUID. UUID can be obtained with data returned from Browse
    /// </summary>
    /// <param name="UUID"></param>
    /// <returns></returns>
    public string Join(string UUID)
    {
        return SendCommand($"join {UUID}");
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
    public string Host(string ServerName) { 
        return SendCommand($"host {ServerName}");
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
