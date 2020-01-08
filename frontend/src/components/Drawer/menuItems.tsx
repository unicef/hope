import DashboardIcon from '@material-ui/icons/DashboardRounded';
import AutorenewIcon from '@material-ui/icons/AutorenewRounded';
import PeopleIcon from '@material-ui/icons/PeopleRounded';
import ListAltRounded from '@material-ui/icons/ListAltRounded';
import FlashOnRounded from '@material-ui/icons/FlashOnRounded';
import AttachMoney from '@material-ui/icons/AttachMoney';
import Feedback from '@material-ui/icons/Feedback';
import TrendingUpRounded from '@material-ui/icons/TrendingUpRounded';
import SupervisedUserCircle from '@material-ui/icons/SupervisedUserCircle';
import SettingsRounded from '@material-ui/icons/SettingsRounded';
import React from 'react';

export const menuItems = [
    {
        name: 'Country Dashboard',
        href: '/#',
        selectedRegexp: /^\/test.*$/,
        icon: <DashboardIcon />,
    },
    {
        name: 'Registration Data Import',
        href: '/#',
        selectedRegexp: /^\/test.*$/,
        icon: <AutorenewIcon />,
    },
    {
        name: 'Population',
        href: '/#',
        selectedRegexp: /^\/test.*$/,
        icon: <PeopleIcon />,
    },
    {
        name: 'Target Population',
        href: '/#',
        selectedRegexp: /^\/test.*$/,
        icon: <ListAltRounded />,
    },
    {
        name: 'Programme Management',
        href: '/programs',
        selectedRegexp: /^\/programs.*$/,
        icon: <FlashOnRounded />,
    },
    {
        name: 'Payment Verification',
        href: '/#',
        selectedRegexp: /^\/test.*$/,
        icon: <AttachMoney />,
    },
    {
        name: 'Grievance and Feedback',
        href: '/#',
        selectedRegexp: /^\/test.*$/,
        icon: <Feedback />,
    },
    {
        name: 'Reporting',
        href: '/#',
        selectedRegexp: /^\/test.*$/,
        icon: <TrendingUpRounded />,
    },
    {
        name: 'User Management',
        href: '/#',
        selectedRegexp: /^\/test.*$/,
        icon: <SupervisedUserCircle />,
    },
    {
        name: 'Settings',
        href: '/#',
        selectedRegexp: /^\/test.*$/,
        icon: <SettingsRounded />,
    },
];