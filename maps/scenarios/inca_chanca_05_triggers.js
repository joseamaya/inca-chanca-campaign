
Trigger.prototype.InitEpilogue = function()
{
	this.icEnded = false;
	this.ICRestrictInca();
	this.ICMessage("Cusco, despu\u00e9s de la victoria. Cusi Yupanqui asume el mando y toma el nombre de Pachac\u00fatec. La tradici\u00f3n lo recuerda como el iniciador del Tawantinsuyu; las cr\u00f3nicas no coinciden en todos los detalles.");
	this.ICObjective("Presencia la asunci\u00f3n de Pachac\u00fatec.");
};

Trigger.prototype.ResumeEpilogue = function()
{
	this.ICRestrictInca();
	this.ICObjective("Presencia la asunci\u00f3n de Pachac\u00fatec.");
};

Trigger.prototype.EpilogueTick = function()
{
	if (this.icEnded)
		return;
	if (this.ICMarker(9041) && this.ICTime() >= 18000)
	{
		this.ICConsume(9041);
		this.ICWin("Cusi Yupanqui se convierte en Pachac\u00fatec. Comienza la expansi\u00f3n del Tawantinsuyu.");
	}
};

{
	const cmpTrigger = Engine.QueryInterface(SYSTEM_ENTITY, IID_Trigger);
	cmpTrigger.RegisterTrigger("OnInitGame", "InitEpilogue", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnDeserialized", "ResumeEpilogue", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnInterval", "EpilogueTick", { "enabled": true, "interval": 1000 });
}
