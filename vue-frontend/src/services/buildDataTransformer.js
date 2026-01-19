// PoB 資料轉換器 - 將 FastAPI 的 PoB 解析結果轉換為前端標準格式

export default class BuildDataTransformer {

    /**
     * 將 FastAPI PoB 解析結果轉換為前端標準格式
     */
    static transformPobDataToBuild(pobData) {
        console.log('轉換 PoB 資料:', pobData)

        // 新架構：使用 StandardizedCharacter 格式
        const characterCore = pobData.character_core || {}
        const equipmentSnapshot = pobData.equipment_snapshot || {}
        const skillSetup = pobData.skill_setup || {}
        const passiveAllocation = pobData.passive_allocation || {}

        // 舊格式兼容（如果API返回舊格式）
        const buildInfo = pobData.build_info || {}
        const config = pobData.config || {}

        // 計算基礎數值
        const stats = this.calculateStatsFromPoB(buildInfo, config)

        return {
            stats: {
                level: characterCore.level || buildInfo.level || 95,
                character_class: characterCore.character_class || buildInfo.class || 'Unknown',
                ascendancy: characterCore.ascendancy || buildInfo.ascendancy || null,
                life: stats.life,
                energy_shield: stats.energy_shield,
                mana: stats.mana,
                dps: stats.dps,
                fire_res: stats.fire_res,
                cold_res: stats.cold_res,
                lightning_res: stats.lightning_res,
                chaos_res: stats.chaos_res
            },
            equipment: this.transformEquipmentSnapshot(equipmentSnapshot),
            skills: this.transformSkillSetup(skillSetup),
            passive_tree: {
                allocated_nodes: passiveAllocation.allocated_nodes || [],
                total_points: passiveAllocation.total_points_used || 0
            },
            source: 'pob_import'
        }
    }

    /**
     * 轉換裝備快照為前端格式
     */
    static transformEquipmentSnapshot(equipmentSnapshot) {
        if (!equipmentSnapshot) return this.getEmptyEquipmentStructure()

        const slots = [
            'weapon_main_hand', 'weapon_off_hand', 'helmet', 'body_armour',
            'gloves', 'boots', 'amulet', 'ring_1', 'ring_2', 'belt',
            'flask_1', 'flask_2', 'flask_3', 'flask_4', 'flask_5'
        ]

        const equipment = {}
        slots.forEach(slot => {
            if (equipmentSnapshot[slot]) {
                equipment[slot] = this.transformEquipmentItem(equipmentSnapshot[slot])
            } else {
                // 沒有裝備時返回預設結構
                equipment[slot] = this.getEmptyEquipmentItem(slot)
            }
        })

        return equipment
    }

    /**
     * 獲取空裝備結構（所有部位都是空的）
     */
    static getEmptyEquipmentStructure() {
        const slots = [
            'weapon_main_hand', 'weapon_off_hand', 'helmet', 'body_armour',
            'gloves', 'boots', 'amulet', 'ring_1', 'ring_2', 'belt',
            'flask_1', 'flask_2', 'flask_3', 'flask_4', 'flask_5'
        ]

        const equipment = {}
        slots.forEach(slot => {
            equipment[slot] = this.getEmptyEquipmentItem(slot)
        })
        return equipment
    }

    /**
     * 獲取空裝備物品（標示沒有裝備的部位）
     */
    static getEmptyEquipmentItem(slot) {
        return {
            slot: slot,
            name: '',
            base_type: '',
            rarity: 'NORMAL',
            item_level: 0,
            quality: 0,
            sockets: {
                total: 0,
                max_links: 0,
                groups: []
            },
            mods: {
                implicit: [],
                explicit: [],
                crafted: [],
                fractured: [],
                enchant: []
            },
            influences: {
                is_elder: false,
                is_shaper: false,
                is_crusader: false,
                is_hunter: false,
                is_redeemer: false,
                is_warlord: false
            },
            is_corrupted: false,
            is_mirrored: false,
            is_synthesised: false,
            has_data: false  // 標示沒有裝備
        }
    }

    /**
     * 轉換單個裝備物品（完整保留後端 EquipmentItem 結構）
     */
    static transformEquipmentItem(item) {
        return {
            // 基本資訊
            slot: item.slot,
            name: item.name || '',
            base_type: item.base_type || '',
            rarity: item.rarity || 'NORMAL',
            item_level: item.item_level || 0,
            quality: item.quality || 0,

            // 插槽系統
            sockets: {
                total: item.total_sockets || 0,
                max_links: item.max_links || 0,
                groups: item.sockets || []
            },

            // 詞綴系統（完整保留）
            mods: {
                implicit: item.implicit_mods || [],
                explicit: item.explicit_mods || [],
                crafted: item.crafted_mods || [],
                fractured: item.fractured_mods || [],
                enchant: item.enchant_mods || []
            },

            // 影響力標記
            influences: {
                is_elder: item.is_elder || false,
                is_shaper: item.is_shaper || false,
                is_crusader: item.is_crusader || false,
                is_hunter: item.is_hunter || false,
                is_redeemer: item.is_redeemer || false,
                is_warlord: item.is_warlord || false
            },

            // 特殊狀態
            is_corrupted: item.is_corrupted || false,
            is_mirrored: item.is_mirrored || false,
            is_synthesised: item.is_synthesised || false,

            // 資料完整性標記
            has_data: true
        }
    }

    /**
     * 轉換技能設置為前端格式
     */
    static transformSkillSetup(skillSetup) {
        if (!skillSetup) {
            return { main_skill_group: null, all_skill_groups: [] }
        }

        return {
            main_skill_group: skillSetup.main_skill_group
                ? this.transformSkillGroup(skillSetup.main_skill_group)
                : null,
            all_skill_groups: (skillSetup.skill_groups || [])
                .map(g => this.transformSkillGroup(g))
        }
    }

    /**
     * 轉換單個技能組（完整保留後端 SkillGroup 結構）
     */
    static transformSkillGroup(group) {
        const gems = group.gems || []

        // ✅ 修正：優先使用後端標記的 main_skill
        // 如果後端有標記 main_skill，根據名稱找到對應的寶石物件
        let mainGem = null
        if (group.main_skill) {
            // 根據後端標記的主技能名稱找到對應寶石
            mainGem = gems.find(g => g.name === group.main_skill && !g.is_support)
        }

        // 如果沒有找到，才使用舊邏輯（找第一個非輔助寶石）
        if (!mainGem) {
            mainGem = gems.find(g => !g.is_support && g.enabled)
        }

        const supportGems = gems.filter(g => g.is_support && g.enabled)

        return {
            // 技能組基本資訊
            label: group.label || 'Skill',
            slot: group.slot || 'Unknown',
            enabled: group.enabled !== undefined ? group.enabled : true,
            link_count: group.link_count || 0,

            // 主技能資訊（簡化版）
            main_skill_name: group.main_skill || (mainGem ? mainGem.name : null),
            support_gem_names: group.support_gems || supportGems.map(g => g.name),

            // 主動技能完整資訊
            main_skill: mainGem ? {
                name: mainGem.name,
                level: mainGem.level || 1,
                quality: mainGem.quality || 0,
                quality_type: mainGem.quality_type || 'DEFAULT',
                is_vaal: mainGem.is_vaal || false,
                is_awakened: mainGem.is_awakened || false,
                enabled: mainGem.enabled !== undefined ? mainGem.enabled : true,
                experience_percent: mainGem.experience_percent || null
            } : null,

            // 輔助寶石完整資訊
            support_gems: supportGems.map(gem => ({
                name: gem.name,
                level: gem.level || 1,
                quality: gem.quality || 0,
                quality_type: gem.quality_type || 'DEFAULT',
                is_awakened: gem.is_awakened || false,
                enabled: gem.enabled !== undefined ? gem.enabled : true,
                experience_percent: gem.experience_percent || null
            })),

            // 所有寶石完整列表（包含未啟用的）
            all_gems: gems.map(gem => ({
                name: gem.name,
                level: gem.level || 1,
                quality: gem.quality || 0,
                quality_type: gem.quality_type || 'DEFAULT',
                is_support: gem.is_support || false,
                is_awakened: gem.is_awakened || false,
                is_vaal: gem.is_vaal || false,
                enabled: gem.enabled !== undefined ? gem.enabled : true,
                experience_percent: gem.experience_percent || null
            }))
        }
    }

    /**
     * 判斷是否為輔助寶石
     */
    static isSupportGem(gemName) {
        const supportKeywords = [
            'Support', 'support',
            'Awakened', 'awakened',
            'Damage on Full Life',
            'Elemental Damage with Attacks',
            'Added Cold Damage',
            'Added Fire Damage',
            'Added Lightning Damage',
            'Increased Critical',
            'Hypothermia',
            'Inspiration',
            'Vicious Projectiles',
            'Multistrike',
            'Melee Physical Damage',
            'Fortify',
            'Concentrated Effect',
            'Increased Area of Effect'
        ]

        return supportKeywords.some(keyword =>
            gemName.toLowerCase().includes(keyword.toLowerCase())
        )
    }

    /**
     * 從 PoB 資料計算角色數值
     */
    static calculateStatsFromPoB(buildInfo, config) {
        const level = buildInfo.level || 90
        const baseLife = 38 + (level - 1) * 12

        // 從 PoB config 中提取計算好的數值（如果有的話）
        const configDPS = this.extractConfigValue(config, ['DPS', 'TotalDPS', 'AverageDamage'])
        const configLife = this.extractConfigValue(config, ['Life', 'TotalLife', 'MaxLife'])
        const configMana = this.extractConfigValue(config, ['Mana', 'TotalMana', 'MaxMana'])
        const configES = this.extractConfigValue(config, ['EnergyShield', 'ES', 'MaxES'])

        return {
            life: configLife || baseLife,
            energy_shield: configES || 0,
            mana: configMana || 300 + (level * 8),
            dps: configDPS || 0,
            fire_res: 75,
            cold_res: 75,
            lightning_res: 75,
            chaos_res: 0
        }
    }

    /**
     * 根據技能資料估算 DPS
     * 注意：此方法已廢棄，僅保留以維持 API 兼容性
     */
    static estimateDpsFromSkills() {
        // 不再提供估算值，僅從 PoB config 中提取
        return null
    }

    /**
     * 從 config 中提取數值
     */
    static extractConfigValue(config, keys) {
        for (const key of keys) {
            if (config[key]) {
                const value = parseFloat(config[key])
                if (!isNaN(value)) return Math.round(value)
            }
        }
        return null
    }

    /**
     * 解析天賦樹 URL（簡化版）
     */
    static parseTreeUrl(url) {
        if (!url || typeof url !== 'string') return []

        // TODO: 實作完整的天賦樹 URL 解析
        return []
    }

    /**
     * 驗證轉換後的資料格式
     */
    static validateBuildData(buildData) {
        const required = ['stats', 'equipment', 'skills', 'passive_tree']
        const missing = required.filter(key => !buildData[key])

        if (missing.length > 0) {
            console.warn('建構資料缺少必要欄位:', missing)
        }

        return missing.length === 0
    }

    /**
     * 生成資料完整性報告（用於偵錯）
     */
    static generateDataReport(buildData) {
        if (!buildData) {
            return '無資料'
        }

        const equipmentCount = Object.keys(buildData.equipment || {}).length
        const skillGroupCount = buildData.skills?.all_skill_groups?.length || 0
        const hasMainSkill = !!buildData.skills?.main_skill_group
        const totalPassivePoints = buildData.passive_tree?.total_points || 0

        const report = {
            基本資訊: {
                等級: buildData.stats?.level,
                職業: buildData.stats?.character_class,
                昇華: buildData.stats?.ascendancy || '未昇華'
            },
            裝備統計: {
                已裝備數量: equipmentCount,
                裝備部位: Object.keys(buildData.equipment || {})
            },
            技能統計: {
                技能組總數: skillGroupCount,
                有主技能: hasMainSkill ? '是' : '否',
                主技能名稱: buildData.skills?.main_skill_group?.main_skill_name || '無'
            },
            天賦統計: {
                已配置點數: totalPassivePoints
            }
        }

        console.log('=== 角色資料完整性報告 ===')
        console.table(report.基本資訊)
        console.table(report.裝備統計)
        console.table(report.技能統計)
        console.table(report.天賦統計)

        return report
    }
}