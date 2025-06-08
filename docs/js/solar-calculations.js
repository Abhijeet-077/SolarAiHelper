// Solar Calculations Module for Solar AI Platform
class SolarCalculator {
    constructor() {
        this.nasaApiBase = 'https://power.larc.nasa.gov/api/temporal/daily/point';
        this.panelSpecs = {
            monocrystalline: {
                efficiency: 0.22,
                power_per_m2: 220,
                degradation_rate: 0.005,
                cost_multiplier: 1.0
            },
            polycrystalline: {
                efficiency: 0.18,
                power_per_m2: 180,
                degradation_rate: 0.007,
                cost_multiplier: 0.85
            },
            'thin-film': {
                efficiency: 0.12,
                power_per_m2: 120,
                degradation_rate: 0.008,
                cost_multiplier: 0.7
            }
        };
    }

    async calculateSolarPotential(roofAnalysis, config) {
        try {
            // Get solar irradiance data
            const solarData = await this.getSolarIrradiance(config.latitude, config.longitude);
            
            // Calculate system specifications
            const systemSpecs = this.calculateSystemSpecs(roofAnalysis, config);
            
            // Calculate energy production
            const energyProduction = this.calculateEnergyProduction(systemSpecs, solarData, roofAnalysis);
            
            // Calculate financial metrics
            const financialMetrics = this.calculateFinancialMetrics(systemSpecs, energyProduction, config);
            
            // Calculate environmental impact
            const environmentalImpact = this.calculateEnvironmentalImpact(energyProduction);

            return {
                success: true,
                system_size_kw: systemSpecs.systemSizeKw,
                panel_count: systemSpecs.panelCount,
                annual_energy_kwh: energyProduction.annualEnergyKwh,
                monthly_energy_kwh: energyProduction.monthlyEnergyKwh,
                daily_energy_kwh: energyProduction.dailyEnergyKwh,
                total_cost: financialMetrics.totalCost,
                annual_savings: financialMetrics.annualSavings,
                payback_years: financialMetrics.paybackYears,
                lifetime_savings: financialMetrics.lifetimeSavings,
                roi_percent: financialMetrics.roiPercent,
                co2_offset_kg: environmentalImpact.co2OffsetKg,
                trees_equivalent: environmentalImpact.treesEquivalent,
                solar_irradiance: solarData.averageIrradiance,
                capacity_factor: energyProduction.capacityFactor
            };
        } catch (error) {
            console.error('Solar calculation failed:', error);
            return this.getFallbackCalculations(roofAnalysis, config);
        }
    }

    async getSolarIrradiance(latitude, longitude) {
        try {
            // Try to fetch from NASA POWER API
            const currentYear = new Date().getFullYear();
            const startDate = `${currentYear - 1}0101`;
            const endDate = `${currentYear - 1}1231`;
            
            const url = `${this.nasaApiBase}?latitude=${latitude}&longitude=${longitude}&start=${startDate}&end=${endDate}&community=RE&parameters=ALLSKY_SFC_SW_DWN&format=JSON`;
            
            // Use a CORS proxy for NASA API
            const proxyUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(url)}`;
            
            const response = await fetch(proxyUrl);
            const data = await response.json();
            
            if (data.contents) {
                const nasaData = JSON.parse(data.contents);
                const irradianceData = nasaData.properties.parameter.ALLSKY_SFC_SW_DWN;
                
                // Calculate average irradiance
                const values = Object.values(irradianceData);
                const averageIrradiance = values.reduce((sum, val) => sum + val, 0) / values.length;
                
                return {
                    averageIrradiance: averageIrradiance,
                    source: 'NASA POWER API',
                    dataQuality: 'High'
                };
            }
        } catch (error) {
            console.log('NASA API unavailable, using estimated values');
        }
        
        // Fallback: estimate based on location
        return this.estimateIrradiance(latitude, longitude);
    }

    estimateIrradiance(latitude, longitude) {
        // Rough estimates based on latitude
        const absLatitude = Math.abs(latitude);
        let baseIrradiance;
        
        if (absLatitude < 25) {
            baseIrradiance = 6.0; // Tropical regions
        } else if (absLatitude < 35) {
            baseIrradiance = 5.5; // Subtropical regions
        } else if (absLatitude < 45) {
            baseIrradiance = 4.8; // Temperate regions
        } else {
            baseIrradiance = 4.0; // Northern regions
        }
        
        // Adjust for specific regions (simplified)
        if (longitude > -130 && longitude < -60 && latitude > 25 && latitude < 50) {
            // Continental US adjustments
            if (latitude > 35 && longitude > -120 && longitude < -100) {
                baseIrradiance += 0.5; // Southwest US bonus
            }
        }
        
        return {
            averageIrradiance: baseIrradiance,
            source: 'Estimated',
            dataQuality: 'Medium'
        };
    }

    calculateSystemSpecs(roofAnalysis, config) {
        const panelSpec = this.panelSpecs[config.panelType] || this.panelSpecs.monocrystalline;
        const usableArea = roofAnalysis.usable_area;
        
        // Calculate maximum possible system size
        const maxSystemSizeKw = (usableArea * panelSpec.power_per_m2) / 1000;
        
        // Adjust based on system size preference
        let systemSizeKw;
        switch (config.systemSizePreference) {
            case 'maximum':
                systemSizeKw = maxSystemSizeKw * 0.95; // 95% of max
                break;
            case 'budget':
                systemSizeKw = maxSystemSizeKw * 0.6; // 60% of max
                break;
            default: // optimal
                systemSizeKw = maxSystemSizeKw * 0.8; // 80% of max
                break;
        }
        
        // Calculate panel count
        const panelPowerKw = panelSpec.power_per_m2 / 1000;
        const panelCount = Math.floor(systemSizeKw / panelPowerKw);
        
        return {
            systemSizeKw: Math.round(systemSizeKw * 100) / 100,
            panelCount: panelCount,
            panelSpec: panelSpec,
            usableArea: usableArea
        };
    }

    calculateEnergyProduction(systemSpecs, solarData, roofAnalysis) {
        const { systemSizeKw, panelSpec } = systemSpecs;
        const { averageIrradiance } = solarData;
        
        // Calculate capacity factor
        const peakSunHours = averageIrradiance;
        const capacityFactor = (peakSunHours / 24) * panelSpec.efficiency * 100;
        
        // Adjust for roof orientation and slope
        let orientationFactor = 1.0;
        switch (roofAnalysis.orientation.toLowerCase()) {
            case 'south':
                orientationFactor = 1.0;
                break;
            case 'southeast':
            case 'southwest':
                orientationFactor = 0.95;
                break;
            case 'east':
            case 'west':
                orientationFactor = 0.85;
                break;
            case 'north':
                orientationFactor = 0.7;
                break;
            default:
                orientationFactor = 0.9;
        }
        
        // Slope factor (optimal around 30-35 degrees)
        const optimalSlope = 32;
        const slopeDifference = Math.abs(roofAnalysis.slope - optimalSlope);
        const slopeFactor = Math.max(0.8, 1 - (slopeDifference / 100));
        
        // Shading factor
        const shadingFactor = 1 - roofAnalysis.shading_factor;
        
        // Calculate annual energy production
        const annualEnergyKwh = systemSizeKw * peakSunHours * 365 * orientationFactor * slopeFactor * shadingFactor;
        
        return {
            annualEnergyKwh: Math.round(annualEnergyKwh),
            monthlyEnergyKwh: Math.round(annualEnergyKwh / 12),
            dailyEnergyKwh: Math.round(annualEnergyKwh / 365 * 100) / 100,
            capacityFactor: Math.round(capacityFactor * 100) / 100,
            orientationFactor: orientationFactor,
            slopeFactor: slopeFactor,
            shadingFactor: shadingFactor
        };
    }

    calculateFinancialMetrics(systemSpecs, energyProduction, config) {
        const { systemSizeKw, panelSpec } = systemSpecs;
        const { annualEnergyKwh } = energyProduction;
        
        // Calculate total system cost
        const baseCostPerWatt = parseFloat(config.installationCost);
        const adjustedCostPerWatt = baseCostPerWatt * panelSpec.cost_multiplier;
        const totalCost = systemSizeKw * 1000 * adjustedCostPerWatt;
        
        // Calculate annual savings
        const electricityRate = parseFloat(config.electricityRate);
        const annualSavings = annualEnergyKwh * electricityRate;
        
        // Calculate payback period
        const paybackYears = totalCost / annualSavings;
        
        // Calculate 25-year lifetime savings
        const systemLifeYears = 25;
        let lifetimeSavings = 0;
        
        for (let year = 1; year <= systemLifeYears; year++) {
            // Account for panel degradation
            const degradationFactor = Math.pow(1 - panelSpec.degradation_rate, year - 1);
            const yearlyProduction = annualEnergyKwh * degradationFactor;
            
            // Account for electricity rate inflation (assume 3% annually)
            const inflatedRate = electricityRate * Math.pow(1.03, year - 1);
            
            lifetimeSavings += yearlyProduction * inflatedRate;
        }
        
        const netLifetimeSavings = lifetimeSavings - totalCost;
        
        // Calculate ROI
        const roiPercent = (netLifetimeSavings / totalCost) * 100;
        
        return {
            totalCost: Math.round(totalCost),
            annualSavings: Math.round(annualSavings),
            paybackYears: Math.round(paybackYears * 100) / 100,
            lifetimeSavings: Math.round(netLifetimeSavings),
            roiPercent: Math.round(roiPercent * 100) / 100
        };
    }

    calculateEnvironmentalImpact(energyProduction) {
        const { annualEnergyKwh } = energyProduction;
        
        // CO2 offset calculation (average grid emission factor)
        const co2FactorKgPerKwh = 0.4; // kg CO2 per kWh (varies by region)
        const annualCo2OffsetKg = annualEnergyKwh * co2FactorKgPerKwh;
        
        // Trees equivalent (one tree absorbs ~22 kg CO2 per year)
        const treesEquivalent = Math.round(annualCo2OffsetKg / 22);
        
        return {
            co2OffsetKg: Math.round(annualCo2OffsetKg),
            treesEquivalent: treesEquivalent,
            annualCo2OffsetKg: Math.round(annualCo2OffsetKg)
        };
    }

    getFallbackCalculations(roofAnalysis, config) {
        // Provide reasonable estimates when API calls fail
        const systemSizeKw = Math.min(roofAnalysis.usable_area * 0.15, 20); // Conservative estimate
        const annualEnergyKwh = systemSizeKw * 1200; // Conservative production estimate
        const totalCost = systemSizeKw * 1000 * parseFloat(config.installationCost);
        const annualSavings = annualEnergyKwh * parseFloat(config.electricityRate);
        
        return {
            success: true,
            system_size_kw: Math.round(systemSizeKw * 100) / 100,
            panel_count: Math.floor(systemSizeKw * 4), // Assume 250W panels
            annual_energy_kwh: Math.round(annualEnergyKwh),
            monthly_energy_kwh: Math.round(annualEnergyKwh / 12),
            daily_energy_kwh: Math.round(annualEnergyKwh / 365 * 100) / 100,
            total_cost: Math.round(totalCost),
            annual_savings: Math.round(annualSavings),
            payback_years: Math.round((totalCost / annualSavings) * 100) / 100,
            lifetime_savings: Math.round(annualSavings * 20 - totalCost),
            roi_percent: Math.round(((annualSavings * 20 - totalCost) / totalCost) * 100),
            co2_offset_kg: Math.round(annualEnergyKwh * 0.4),
            trees_equivalent: Math.round(annualEnergyKwh * 0.4 / 22),
            solar_irradiance: 4.5,
            capacity_factor: 18.5,
            source: 'Estimated (Offline)'
        };
    }

    // Utility methods
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }

    formatNumber(number) {
        return new Intl.NumberFormat('en-US').format(Math.round(number));
    }

    formatPercentage(percentage) {
        return `${percentage.toFixed(1)}%`;
    }
}

// Export for use in other modules
window.SolarCalculator = SolarCalculator;
