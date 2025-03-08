import {
    Card,
    CardHeader,
    CardBody,
    Table,
    TableHeader,
    TableColumn,
    TableBody,
    TableRow,
    TableCell,
    Button,
    Chip
} from "@nextui-org/react";
import { History, ArrowRight } from 'lucide-react';

import { useWebSocket } from '@/hooks/useWebSocket';
import { Props } from "./types";

export default function AdminPanel({ stations, onShowRoute }: Props) {
    const { routeHistory } = useWebSocket();

    if (!routeHistory?.length) {
        return null;
    }

    return (
        <Card className="glass-effect responsive-card">
            <CardHeader className="flex gap-3">
                <History className="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
                <div className="flex flex-col">
                    <p className="text-lg md:text-xl font-semibold">Historial de rutas</p>
                    <p className="text-xs md:text-sm text-gray-500">
                        Últimas rutas calculadas
                    </p>
                </div>
            </CardHeader>
            <CardBody>
                <div className="overflow-x-auto responsive-table">
                    <Table aria-label="Historial de rutas">
                        <TableHeader>
                            <TableColumn className="text-xs md:text-sm">ORIGEN</TableColumn>
                            <TableColumn className="text-xs md:text-sm">DESTINO</TableColumn>
                            <TableColumn className="text-xs md:text-sm">TIEMPO</TableColumn>
                            <TableColumn className="text-xs md:text-sm">LÍNEAS</TableColumn>
                            <TableColumn className="text-xs md:text-sm">ACCIONES</TableColumn>
                        </TableHeader>
                        <TableBody>
                            {routeHistory.map((route, index) => (
                                <TableRow key={index} className="text-xs md:text-sm">
                                    <TableCell>{route.path[0]}</TableCell>
                                    <TableCell>{route.path[route.path.length - 1]}</TableCell>
                                    <TableCell>{route.estimated_time} min</TableCell>
                                    <TableCell>
                                        <div className="flex flex-wrap gap-1">
                                            {route.lines.map((line, i) => (
                                                <Chip 
                                                    key={i} 
                                                    size="sm" 
                                                    variant="flat"
                                                    className="text-xs"
                                                >
                                                    {line}
                                                </Chip>
                                            ))}
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <Button
                                            size="sm"
                                            color="primary"
                                            variant="flat"
                                            onPress={() => onShowRoute(route)}
                                            startContent={<ArrowRight className="w-3 h-3 md:w-4 md:h-4" />}
                                            className="text-xs md:text-sm touch-target"
                                        >
                                            Ver ruta
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            </CardBody>
        </Card>
    );
} 