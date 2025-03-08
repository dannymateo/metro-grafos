import { useState } from 'react';
import { Button, Chip, Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@nextui-org/react';
import { AlertCircle, Clock } from 'lucide-react';

import { WeatherImpact } from '@/types';
import { WeatherDetailsContent } from './WeatherDetailsContent/WeatherDetailsContent';

export const WeatherImpactInfo = ({ weatherImpacts }: { weatherImpacts: WeatherImpact[] }) => {
    const [showDetails, setShowDetails] = useState(false);

    const maxImpact = Math.max(...weatherImpacts.map(impact => 
        Math.max(impact.conditions.origin.impact, impact.conditions.destination.impact)
    ));

    return (
        <div className="mt-4">
            <div className="bg-gradient-to-r from-blue-50 to-yellow-50 rounded-lg p-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <AlertCircle className="w-5 h-5 text-yellow-500" />
                        <div>
                            <div className="text-sm font-medium text-gray-700">Clima en ruta</div>
                            <div className="text-xs text-gray-500">{weatherImpacts.length} segmentos afectados</div>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <Chip
                            size="sm"
                            variant="flat"
                            color={maxImpact > 30 ? "danger" : maxImpact > 20 ? "warning" : "success"}
                            className="text-xs"
                            startContent={<Clock className="w-3 h-3" />}
                        >
                            +{maxImpact}% tiempo
                        </Chip>
                        <Button
                            size="sm"
                            variant="light"
                            onPress={() => setShowDetails(true)}
                        >
                            Ver detalles
                        </Button>
                    </div>
                </div>
            </div>

            <Modal 
                isOpen={showDetails} 
                onClose={() => setShowDetails(false)}
                size="md"
            >
                <ModalContent>
                    <ModalHeader>Detalles del clima en la ruta</ModalHeader>
                    <ModalBody>
                        <WeatherDetailsContent weatherImpacts={weatherImpacts} />
                    </ModalBody>
                    <ModalFooter>
                        <Button color="primary" onPress={() => setShowDetails(false)}>
                            Cerrar
                        </Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </div>
    );
}; 