import Login from './Login/Login.svelte';
import NuevoPedido from './User/NuevoPedido.svelte';
import DetallesPedido from './User/DetallesPedido.svelte';
import Pedidos from './User/Pedidos.svelte';
import PedidosAdmin from './Admin/PedidosAdmin.svelte';
import Sucursales from './Admin/Sucursales.svelte';
import Camiones from './Admin/Camiones.svelte';
import NuevoPedidoAdmin from './Admin/CRUD/NuevoPedidoAdmin.svelte';

const routes = {
    '/':Login,
    '/nuevopedido':NuevoPedido,
    '/pedidos': Pedidos,
    '/detallespedido/:id': DetallesPedido,
    '/pedidosadmin': PedidosAdmin,
    '/sucursales': Sucursales,
    '/camiones':Camiones,
    '/nuevopedidoadmin':NuevoPedidoAdmin
};

export default routes;