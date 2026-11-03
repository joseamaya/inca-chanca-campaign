
Trigger.prototype.InitMission4 = function()
{
	this.icEnded = false;
	this.ICRestrictInca();
	this.ICMessage("La guerra se traslada al pa\u00eds chanca, hacia Andahuaylas y el Apur\u00edmac. Toma la fortaleza de altura y derrota o captura a Anccu Huallo.");
	this.ICObjective(this.M4Objective());
};

Trigger.prototype.ResumeMission4 = function()
{
	this.ICRestrictInca();
	this.ICObjective(this.M4Objective());
};

Trigger.prototype.M4Objective = function()
{
	return "Avanza hacia la fortaleza chanca y toma su centro c\u00edvico. Anccu Huallo debe ser derrotado o capturado.";
};

Trigger.prototype.Mission4Tick = function()
{
	if (this.icEnded)
		return;
	if (!this.ICAliveOwned(1000, 1))
	{
		this.ICLose("Cusi Yupanqui ha ca\u00eddo en territorio chanca.");
		return;
	}
	const t = this.ICTime();
	if (this.ICMarker(9031) && t >= 30000)
	{
		this.ICConsume(9031);
		this.ICMessage("El ej\u00e9rcito inca avanza por el valle. La fortaleza chanca domina el paso.");
		this.ICAttack(1, 780, 280);
		this.ICAttack(2, 300, 760);
	}
	const centreTaken = !this.ICAlive(2100) || TriggerHelper.GetOwner(2100) === 1;
	const anccuDown = !this.ICAlive(2003) || TriggerHelper.GetOwner(2003) === 1;
	if (centreTaken && anccuDown)
	{
		this.ICMessage("La fortaleza ha ca\u00eddo. Los supervivientes chancas se incorporan al ej\u00e9rcito inca, como ocurri\u00f3 tras la victoria.");
		this.ICWin("Has conquistado el pa\u00eds chanca y consolidado el poder de Cusco.");
		return;
	}
	if (this.ICMarker(9032) && t >= 300000)
	{
		this.ICConsume(9032);
		this.ICMessage("La fortaleza sigue en pie. Toma el centro c\u00edvico y derrota o captura a Anccu Huallo.");
	}
};

{
	const cmpTrigger = Engine.QueryInterface(SYSTEM_ENTITY, IID_Trigger);
	cmpTrigger.RegisterTrigger("OnInitGame", "InitMission4", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnDeserialized", "ResumeMission4", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnInterval", "Mission4Tick", { "enabled": true, "interval": 1000 });
}
