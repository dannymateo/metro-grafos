import { Chip } from "@nextui-org/react";

import { WeatherImpact } from "@/types";
import { getWeatherIcon } from "@/utils/weather";

export const WeatherDetailsContent = ({ weatherImpacts }: { weatherImpacts: WeatherImpact[] }) => {
    return (
        <div className="space-y-2">
            {weatherImpacts.map((impact, idx) => (
                <div 
                    key={idx} 
                    className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 transition-all duration-200"
                >
                    <div className="flex items-center gap-1.5">
                        <span className="text-sm font-medium">
                            {impact.segment[0]} → {impact.segment[1]}
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="flex items-center gap-1.5 bg-gray-50 px-2 py-1 rounded-full">
                            <span className="text-xs">{impact.conditions.origin.weather}</span>
                            <span className="text-base">{getWeatherIcon(impact.conditions.origin.weather)}</span>
                        </div>
                        <Chip 
                            size="sm" 
                            variant="flat" 
                            color={impact.conditions.origin.impact > 20 ? "warning" : "success"}
                        >
                            +{impact.conditions.origin.impact}%
                        </Chip>
                    </div>
                </div>
            ))}
        </div>
    );
};