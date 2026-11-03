
Trigger.prototype.InitMission1 = function()
{
	this.icEnded = false;
	this.ICRestrictInca();
	this.ICMessage("Cusco, c. 1438. Los chancas han enviado mensajeros exigiendo la sumisi\u00f3n del Curacazgo. Viracocha Inca e Inca Urco abandonan la ciudad; Cusi Yupanqui decide quedarse y defenderla. Las unidades imperiales tard\u00edas, los barcos, la maravilla y los h\u00e9roes de otras \u00e9pocas est\u00e1n deshabilitados en esta campa\u00f1a.");
	this.ICObjective(this.M1Objective());
};

Trigger.prototype.ResumeMission1 = function()
{
	this.ICRestrictInca();
	this.ICObjective(this.M1Objective());
};

Trigger.prototype.M1Objective = function()
{
	if (!this.ICMarker(9004))
		return "Resiste el asalto final.";
	if (!this.ICMarker(9003))
		return "Resiste la segunda oleada.";
	if (!this.ICMarker(9002))
		return "Resiste la primera oleada.";
	return "Re\u00fane recursos, fortifica Cusco y resiste las incursiones chancas.";
};

Trigger.prototype.Mission1Tick = function()
{
	if (this.icEnded)
		return;
	if (!this.ICAliveOwned(1000, 1))
	{
		this.ICLose("Cusi Yupanqui ha ca\u00eddo. La defensa de Cusco se desmorona.");
		return;
	}
	if (!this.ICAliveOwned(1100, 1))
	{
		this.ICLose("El centro c\u00edvico de Cusco ha ca\u00eddo o ha sido destruido.");
		return;
	}
	const t = this.ICTime();
	if (this.ICMarker(9001) && t >= 8000)
	{
		this.ICConsume(9001);
		if (this.ICAlive(1001))
			Engine.DestroyEntity(1001);
		if (this.ICAlive(1002))
			Engine.DestroyEntity(1002);
		this.ICMessage("Viracocha Inca e Inca Urco han huido. Cusi Yupanqui queda al mando de la defensa. Las cr\u00f3nicas difieren sobre estos hechos.");
	}
	if (this.ICMarker(9002) && t >= 60000)
	{
		this.ICConsume(9002);
		this.ICMessage("Primera incursi\u00f3n chanca: una columna avanza desde el norte.");
		this.ICSpawn(2, "units/chanca/infantry_maceman_b", 820, 260, 8, 0);
		this.ICSpawn(2, "units/chanca/infantry_slinger_b", 840, 280, 4, 0);
		this.ICAttack(2, 400, 560);
	}
	if (this.ICMarker(9003) && t >= 150000)
	{
		this.ICConsume(9003);
		this.ICMessage("Segunda oleada: los chancas presionan por el este. Los aliados canas se suman a la defensa.");
		this.ICSpawn(2, "units/chanca/infantry_maceman_b", 760, 240, 10, 0);
		this.ICSpawn(2, "units/chanca/infantry_axeman_b", 760, 280, 5, 0);
		this.ICAttack(2, 400, 560);
		this.ICAttack(3, 820, 250);
	}
	if (this.ICMarker(9004) && t >= 240000)
	{
		this.ICConsume(9004);
		this.ICMessage("Tercera oleada: el grueso de la hueste chanca ataca Cusco.");
		this.ICSpawn(2, "units/chanca/infantry_maceman_b", 860, 300, 12, 0);
		this.ICSpawn(2, "units/chanca/infantry_slinger_b", 860, 340, 6, 0);
		this.ICSpawn(2, "units/chanca/infantry_spearman_b", 820, 320, 6, 0);
		this.ICAttack(2, 400, 560);
	}
	if (this.ICMarker(9005) && t >= 360000)
	{
		this.ICConsume(9005);
		if (this.ICAliveOwned(1100, 1) && this.ICAliveOwned(1000, 1))
		{
			this.ICMessage("Cusco resiste. La victoria en Yahuar Pampa a\u00fan est\u00e1 por venir.");
			this.ICWin("Has defendido Cusco y rechazado las incursiones chancas.");
		}
	}
};

{
	const cmpTrigger = Engine.QueryInterface(SYSTEM_ENTITY, IID_Trigger);
	cmpTrigger.RegisterTrigger("OnInitGame", "InitMission1", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnDeserialized", "ResumeMission1", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnInterval", "Mission1Tick", { "enabled": true, "interval": 1000 });
}
