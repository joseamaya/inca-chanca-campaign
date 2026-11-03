
Trigger.prototype.InitMission2 = function()
{
	this.icEnded = false;
	this.ICRestrictInca();
	this.ICMessage("Cusco est\u00e1 rodeado. La tradici\u00f3n recuerda la defensa de Carmenca y Chocos-Cachona. Protege el centro c\u00edvico y el santuario, y conserva con vida a Cusi Yupanqui.");
	this.ICObjective(this.M2Objective());
};

Trigger.prototype.ResumeMission2 = function()
{
	this.ICRestrictInca();
	this.ICObjective(this.M2Objective());
};

Trigger.prototype.M2Objective = function()
{
	if (!this.ICMarker(9014))
		return "Resiste la oleada final.";
	if (!this.ICMarker(9013))
		return "Resiste la tercera oleada.";
	if (!this.ICMarker(9012))
		return "Resiste la segunda oleada.";
	if (!this.ICMarker(9011))
		return "Resiste la primera oleada.";
	return "Resiste las oleadas chancas y protege el centro c\u00edvico y el santuario durante 7 minutos.";
};

Trigger.prototype.Mission2Tick = function()
{
	if (this.icEnded)
		return;
	if (!this.ICAliveOwned(1000, 1))
	{
		this.ICLose("Cusi Yupanqui ha ca\u00eddo durante el asedio.");
		return;
	}
	if (!this.ICAliveOwned(1100, 1))
	{
		this.ICLose("El centro c\u00edvico de Cusco ha ca\u00eddo.");
		return;
	}
	if (!this.ICAliveOwned(1101, 1))
	{
		this.ICLose("El santuario de Cusco ha ca\u00eddo o ha sido destruido.");
		return;
	}
	const t = this.ICTime();
	if (this.ICMarker(9011) && t >= 45000)
	{
		this.ICConsume(9011);
		this.ICMessage("Los chancas atacan el flanco norte.");
		this.ICSpawn(2, "units/chanca/infantry_maceman_b", 700, 300, 10, 0);
		this.ICSpawn(2, "units/chanca/infantry_slinger_b", 720, 330, 5, 0);
		this.ICAttack(2, 450, 560);
	}
	if (this.ICMarker(9012) && t >= 120000)
	{
		this.ICConsume(9012);
		this.ICMessage("Segunda oleada: ataque coordinado por el sur. Astoy Huaraca dirige a los veteranos.");
		this.ICSpawn(2, "units/chanca/infantry_maceman_b", 700, 780, 12, 0);
		this.ICAttack(2, 450, 560);
	}
	if (this.ICMarker(9013) && t >= 210000)
	{
		this.ICConsume(9013);
		this.ICMessage("Tercera oleada: Tomay Huaraca presiona el este. La ciudad resiste.");
		this.ICSpawn(2, "units/chanca/infantry_spearman_b", 760, 550, 8, 0);
		this.ICSpawn(2, "units/chanca/infantry_axeman_b", 760, 580, 6, 0);
		this.ICAttack(2, 450, 560);
	}
	if (this.ICMarker(9014) && t >= 300000)
	{
		this.ICConsume(9014);
		this.ICMessage("Oleada final: Anccu Huallo lanza el asalto decisivo.");
		this.ICSpawn(2, "units/chanca/infantry_maceman_b", 760, 800, 14, 0);
		this.ICSpawn(2, "units/chanca/infantry_slinger_b", 780, 820, 7, 0);
		this.ICSpawn(2, "units/chanca/infantry_axeman_b", 740, 820, 6, 0);
		this.ICAttack(2, 450, 560);
	}
	if (this.ICMarker(9015) && t >= 420000)
	{
		this.ICConsume(9015);
		if (this.ICAliveOwned(1100, 1) && this.ICAliveOwned(1101, 1) && this.ICAliveOwned(1000, 1))
		{
			this.ICMessage("El asedio ha sido rechazado. Cusco sigue en pie.");
			this.ICWin("Has resistido el asedio chanca y salvado Cusco.");
		}
	}
};

Trigger.prototype.M2OnOwnershipChanged = function(msg)
{
	if (msg.entity === 2100 && msg.to === 1)
	{
		this.ICMessage("Has tomado el centro c\u00edvico chanca. El asedio se quiebra.");
		this.ICWin("Has contraatacado y roto el asedio chanca.");
	}
};

{
	const cmpTrigger = Engine.QueryInterface(SYSTEM_ENTITY, IID_Trigger);
	cmpTrigger.RegisterTrigger("OnInitGame", "InitMission2", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnDeserialized", "ResumeMission2", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnOwnershipChanged", "M2OnOwnershipChanged", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnInterval", "Mission2Tick", { "enabled": true, "interval": 1000 });
}
