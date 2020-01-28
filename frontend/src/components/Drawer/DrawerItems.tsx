import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import { Link } from 'react-router-dom';
import React from 'react';
import { menuItems } from './menuItems';

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
            component={Link}
            key={item.name}
            to={item.href}
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
