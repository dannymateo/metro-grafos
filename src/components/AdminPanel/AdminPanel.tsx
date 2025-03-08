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
        <Card className="bg-white/70 backdrop-blur-md shadow-lg border-none">
            <CardHeader className="flex gap-3">
                <History className="w-6 h-6 text-blue-600" />
                <div className="flex flex-col">
                    <p className="text-xl font-semibold">Historial de rutas</p>
                    <p className="text-small text-gray-500">
                        Últimas rutas calculadas
                    </p>
                </div>
            </CardHeader>
            <CardBody>
                <Table aria-label="Historial de rutas">
                    <TableHeader>
                        <TableColumn>ORIGEN</TableColumn>
                        <TableColumn>DESTINO</TableColumn>
                        <TableColumn>TIEMPO</TableColumn>
                        <TableColumn>LÍNEAS</TableColumn>
                        <TableColumn>ACCIONES</TableColumn>
                    </TableHeader>
                    <TableBody>
                        {routeHistory.map((route, index) => (
                            <TableRow key={index}>
                                <TableCell>{route.path[0]}</TableCell>
                                <TableCell>{route.path[route.path.length - 1]}</TableCell>
                                <TableCell>{route.estimated_time} min</TableCell>
                                <TableCell>
                                    <div className="flex gap-1">
                                        {route.lines.map((line, i) => (
                                            <Chip key={i} size="sm" variant="flat">
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
                                        startContent={<ArrowRight className="w-4 h-4" />}
                                    >
                                        Ver ruta
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardBody>
        </Card>
    );
} 