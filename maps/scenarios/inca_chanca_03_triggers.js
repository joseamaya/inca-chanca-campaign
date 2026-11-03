
Trigger.prototype.InitMission3 = function()
{
	this.icEnded = false;
	this.ICRestrictInca();
	this.ICMessage("Yahuar Pampa, la pampa de sangre. Las cr\u00f3nicas exageran las cifras, pero coinciden en que la batalla decidi\u00f3 el futuro del Cusco. La leyenda de los pururaucas se contar\u00e1 como tradici\u00f3n, no como hecho comprobado.");
	this.ICObjective(this.M3Objective());
};

Trigger.prototype.ResumeMission3 = function()
{
	this.ICRestrictInca();
	this.ICObjective(this.M3Objective());
};

Trigger.prototype.M3Objective = function()
{
	if (TriggerHelper.GetOwner(2000) === 1)
		return "La momia de Uscovilca est\u00e1 en tu poder. Elimina o captura a los capitanes chancas.";
	return "Mant\u00e9n la l\u00ednea, elimina o captura a los capitanes chancas y toma la momia de Uscovilca.";
};

Trigger.prototype.Mission3Tick = function()
{
	if (this.icEnded)
		return;
	if (!this.ICAliveOwned(1000, 1))
	{
		this.ICLose("Cusi Yupanqui ha ca\u00eddo en Yahuar Pampa.");
		return;
	}
	const t = this.ICTime();
	if (this.ICMarker(9021) && t >= 30000)
	{
		this.ICConsume(9021);
		this.ICMessage("Las dos huestes avanzan. Cusi Yupanqui arenga a sus hombres.");
		this.ICAttack(2, 420, 512);
		this.ICAttack(1, 700, 512);
		this.ICAttack(3, 700, 512);
	}
	if (this.ICMarker(9022) && t >= 180000)
	{
		this.ICConsume(9022);
		this.ICMessage("Seg\u00fan la tradici\u00f3n, las piedras del campo (pururaucas) se levantaron para luchar junto a los incas. Es una leyenda recogida por las cr\u00f3nicas, no un hecho comprobado. Un contingente de reserva se suma al combate.");
		this.ICSpawn(1, "units/inca/infantry_spearman_b", 420, 512, 8, 0);
		this.ICAttack(1, 740, 512);
	}
	if (this.ICAllHeroesDead([2001, 2002, 2003]))
	{
		this.ICMessage("Los capitanes chancas han ca\u00eddo. La confederaci\u00f3n se desmorona.");
		this.ICWin("Has ganado en Yahuar Pampa y abierto el camino al Tawantinsuyu.");
		return;
	}
	if (this.ICMarker(9023) && t >= 360000)
	{
		this.ICConsume(9023);
		this.ICMessage("La batalla contin\u00faa. Elimina o captura a los capitanes chancas para romper la confederaci\u00f3n.");
	}
};

Trigger.prototype.M3OnOwnershipChanged = function(msg)
{
	if (msg.entity === 2000 && msg.to === 1)
	{
		this.ICMessage("Has capturado la momia de Uscovilca. La moral chanca se quiebra; seg\u00fan Sarmiento de Gamboa, era llevada como reliquia.");
		this.ICRetreat(2, 820, 512);
		this.ICAttack(1, 740, 512);
	}
};

{
	const cmpTrigger = Engine.QueryInterface(SYSTEM_ENTITY, IID_Trigger);
	cmpTrigger.RegisterTrigger("OnInitGame", "InitMission3", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnDeserialized", "ResumeMission3", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnOwnershipChanged", "M3OnOwnershipChanged", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnInterval", "Mission3Tick", { "enabled": true, "interval": 1000 });
}
