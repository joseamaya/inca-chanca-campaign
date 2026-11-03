
// Funciones comunes de la campa\u00f1a inca-chanca.
Trigger.prototype.ICMessage = function(text)
{
	const cmpGuiInterface = Engine.QueryInterface(SYSTEM_ENTITY, IID_GuiInterface);
	cmpGuiInterface.PushNotification({
		"type": "tutorial",
		"players": [1],
		"instructions": [text]
	});
};

Trigger.prototype.ICObjective = function(text)
{
	this.ICMessage("OBJETIVO: " + text);
};

Trigger.prototype.ICWin = function(text)
{
	if (this.icEnded)
		return;
	this.icEnded = true;
	const cmpEndGameManager = Engine.QueryInterface(SYSTEM_ENTITY, IID_EndGameManager);
	cmpEndGameManager.MarkPlayerAndAlliesAsWon(1, () => text, () => "Has sido derrotado.");
};

Trigger.prototype.ICLose = function(text)
{
	if (this.icEnded)
		return;
	this.icEnded = true;
	TriggerHelper.DefeatPlayer(1, text);
};

Trigger.prototype.ICTime = function()
{
	return TriggerHelper.GetTime();
};

// Los marcadores son trigger points invisibles colocados en el mapa.
Trigger.prototype.ICMarker = function(uid)
{
	return !!Engine.QueryInterface(uid, IID_Position);
};

Trigger.prototype.ICConsume = function(uid)
{
	if (!this.ICMarker(uid))
		return false;
	Engine.DestroyEntity(uid);
	return true;
};

// Restricciones hist\u00f3ricas para el jugador inca en 1438.
Trigger.prototype.ICRestrictInca = function()
{
	const cmpPlayerManager = Engine.QueryInterface(SYSTEM_ENTITY, IID_PlayerManager);
	const playerEnt = cmpPlayerManager.GetPlayerByID(1);
	const cmpPlayer = Engine.QueryInterface(playerEnt, IID_Player);
	if (!cmpPlayer)
		return;
	const disabled = [
		"units/inca/mechanical_siege_ram",
		"units/inca/champion_imperial",
		"units/inca/champion_guaranga_kamayuk",
		"units/inca/champion_apusquin_rantin",
		"units/inca/champion_apusquin _rantin",
		"units/inca/champion_pachac_kamayuk",
		"units/inca/champion_infantry_archer",
		"units/inca/champion_pikeman",
		"units/inca/hero_pachacutec",
		"units/inca/hero_sapa_inca",
		"units/inca/hero_sinchi_roca",
		"units/inca/hero_capac_yupanqui",
		"units/inca/ship_arrow",
		"units/inca/ship_fishing",
		"units/inca/ship_merchant",
		"units/inca/ship_scout",
		"units/inca/infantry_archer_merc_a",
		"units/inca/infantry_archer_merc_b",
		"units/inca/infantry_archer_merc_e",
		"units/inca/infantry_maceman_merc_a",
		"units/inca/infantry_maceman_merc_b",
		"units/inca/infantry_maceman_merc_e",
		"units/inca/infantry_maceman2_merc_a",
		"units/inca/infantry_maceman2_merc_b",
		"units/inca/infantry_maceman2_merc_e",
		"structures/inca/dock",
		"structures/inca/wonder",
		"structures/inca/military_colony"
	];
	for (const t of disabled)
		cmpPlayer.AddDisabledTemplate(t);
};

Trigger.prototype.ICSpawn = function(player, template, x, z, count, angle)
{
	const out = [];
	for (let i = 0; i < count; ++i)
	{
		const ent = Engine.AddEntity(template);
		if (!ent)
			continue;
		const cmpPos = Engine.QueryInterface(ent, IID_Position);
		const cmpOwn = Engine.QueryInterface(ent, IID_Ownership);
		if (!cmpPos)
		{
			Engine.DestroyEntity(ent);
			continue;
		}
		cmpPos.JumpTo(x + (i % 4) * 4, z + Math.floor(i / 4) * 4);
		cmpPos.SetYRotation(angle || 0);
		if (cmpOwn)
			cmpOwn.SetOwner(player);
		out.push(ent);
	}
	return out;
};

Trigger.prototype.ICAttack = function(player, x, z)
{
	const ents = TriggerHelper.GetPlayerEntitiesByClass(player, "Soldier");
	if (!ents.length)
		return;
	ProcessCommand(player, {
		"type": "attack-walk",
		"entities": ents,
		"x": x,
		"z": z,
		"targetClasses": { "attack": ["Unit", "Structure"] },
		"allowCapture": true,
		"queued": false
	});
};

Trigger.prototype.ICRetreat = function(player, x, z)
{
	const ents = TriggerHelper.GetPlayerEntitiesByClass(player, "Soldier");
	if (!ents.length)
		return;
	ProcessCommand(player, {
		"type": "walk",
		"entities": ents,
		"x": x,
		"z": z,
		"queued": false
	});
};

Trigger.prototype.ICAlive = function(uid)
{
	const cmpHealth = Engine.QueryInterface(uid, IID_Health);
	return !!cmpHealth && cmpHealth.GetHitpoints() > 0;
};

Trigger.prototype.ICOwner = function(uid)
{
	return TriggerHelper.GetOwner(uid);
};

Trigger.prototype.ICAliveOwned = function(uid, player)
{
	return this.ICAlive(uid) && this.ICOwner(uid) === player;
};

Trigger.prototype.ICCount = function(player, template)
{
	const cmpTemplateManager = Engine.QueryInterface(SYSTEM_ENTITY, IID_TemplateManager);
	let n = 0;
	for (const ent of TriggerHelper.GetEntitiesByPlayer(player))
	{
		if (cmpTemplateManager.GetCurrentTemplateName(ent) === template && this.ICAlive(ent))
			++n;
	}
	return n;
};

Trigger.prototype.ICAllHeroesDead = function(uids)
{
	return uids.every(uid => !this.ICAlive(uid) || TriggerHelper.GetOwner(uid) === 1);
};
