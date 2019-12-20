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
    icon: <DashboardIcon />,
  },
  {
    name: 'Registration Data Import',
    icon: <AutorenewIcon />,
  },
  {
    name: 'Population',
    icon: <PeopleIcon />,
  },
  {
    name: 'Target Population',
    icon: <ListAltRounded />,
  },
  {
    name: 'Programme Management',
    icon: <FlashOnRounded />,
  },
  {
    name: 'Payment Verification',
    icon: <AttachMoney />,
  },
  {
    name: 'Grievance and Feedback',
    icon: <Feedback />,
  },
  {
    name: 'Reporting',
    icon: <TrendingUpRounded />,
  },
  {
    name: 'User Management',
    icon: <SupervisedUserCircle />,
  },
  {
    name: 'Settings',
    icon: <SettingsRounded />,
  },
];
export function DrawerItems(): React.ReactElement {
  return (
    <div>
      {menuItems.map((item) => {
        return (
          <ListItem button>
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.name} />
          </ListItem>
        );
      })}
    </div>
  );
}
