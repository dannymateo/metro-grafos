import { Card, CardBody } from '@nextui-org/react';

import { Route } from "@/types";
import { TimeAndDistanceInfo } from './TimeAndDistanceInfo';
import { LinesInfo } from './LinesInfo';
import { TransbordosInfo } from './TransbordosInfo/TransbordosInfo';
import { WeatherImpactInfo } from '@/components/WeatherDetailsContent';

export const RouteInfo = ({ route }: { route: Route }) => {
    return (
        <Card className="bg-gradient-to-br from-blue-50 to-white border-none shadow-sm">
            <CardBody className="space-y-4">
                <TimeAndDistanceInfo route={route} />
                <LinesInfo route={route} />
                <TransbordosInfo route={route} />
                {route.weather_impacts && (
                    <WeatherImpactInfo weatherImpacts={route.weather_impacts} />
                )}
            </CardBody>
        </Card>
    );
}; 