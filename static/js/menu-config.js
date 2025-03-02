// 菜单配置
const menuConfig = [
    {
        id: 'dashboard',
        title: '仪表盘',
        icon: 'bi-speedometer2',
        url: '/dashboard',
        adminOnly: false
    },
    {
        id: 'user-management',
        title: '用户管理',
        icon: 'bi-people',
        url: '#',
        adminOnly: true
    },
    {
        id: 'snake-game',
        title: '贪吃蛇游戏',
        icon: 'bi-controller',
        url: '/snake-game',
        adminOnly: false
    }
    // 可以在这里添加更多菜单项
];

// 导出菜单配置
module.exports = menuConfig;