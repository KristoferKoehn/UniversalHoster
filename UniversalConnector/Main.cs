using Godot;
using System;
using System.Collections.Generic;

public partial class Main : Node2D
{
	UniversalConnector connector;
	Tree tree;
	LineEdit serverName;
	Timer timer;

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		connector = new UniversalConnector("127.0.0.1", 9999);
		tree = this.GetNode<Tree>("Control/Panel/Tree");
        serverName = this.GetNode<LineEdit>("Control/Panel/ServerName");
        tree.CreateItem();
		tree.HideRoot = true;
		timer = new Timer();
		this.AddChild(timer);
		timer.Timeout += updateTree;
		timer.Start(2);

    }

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
		
		
	}

	public void _on_host_pressed()
	{
		if (serverName.Text.Length > 0)
		{
			connector.Host(serverName.Text);
		}
	}

	public void updateTree()
	{
		tree.Clear();
		tree.CreateItem();

        List<string> serverList = connector.Browse();
		if (serverList.Count < 1)
		{
			return;
		} 
        foreach (string server in serverList)
        {
            string[] strings = server.Split(new char[] { ' ' }, 2);
            TreeItem ti = tree.CreateItem();
            ti.SetText(0, strings[0]);
            ti.SetText(1, strings[1]);
        }
    }

	public void _on_join_pressed()
	{
		if (tree.GetSelected() is not null)
		{
			TreeItem selection = tree.GetSelected();
			connector.Join(selection.GetText(0));
		}
	}

}
