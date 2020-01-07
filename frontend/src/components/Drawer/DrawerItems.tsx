import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import DashboardIcon from '@material-ui/icons/DashboardRounded';
import ListItemText from '@material-ui/core/ListItemText';
import AutorenewIcon from '@material-ui/icons/AutorenewRounded';
import PeopleIcon from '@material-ui/icons/PeopleRounded';
import ListAltRounded from '@material-ui/icons/ListAltRounded';
import FlashOnRounded from '@material-ui/icons/FlashOnRounded';
import AttachMoney from '@material-ui/icons/AttachMoney';
import Feedback from '@material-ui/icons/Feedback';
import SupervisedUserCircle from '@material-ui/icons/SupervisedUserCircle';
import SettingsRounded from '@material-ui/icons/SettingsRounded';
import TrendingUpRounded from '@material-ui/icons/TrendingUpRounded';
import React from 'react';

const menuItems = [
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
interface Props {
  currentLocation: string;
}
export function DrawerItems({ currentLocation }: Props): React.ReactElement {
  return (
    <div>
      {menuItems.map((item) => {
        return (
          <ListItem
            button
            component='a'
            key={item.name}
            href={item.href}
            selected={Boolean(item.selectedRegexp.exec(currentLocation))}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.name} />
          </ListItem>
        );
      })}
    </div>
  );
}
