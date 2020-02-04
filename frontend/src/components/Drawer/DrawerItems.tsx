import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import { Link } from 'react-router-dom';
import React from 'react';
import { menuItems } from './menuItems';
import { useBusinessArea } from '../../hooks/useBusinessArea';

interface Props {
  currentLocation: string;
}
export function DrawerItems({ currentLocation }: Props): React.ReactElement {
  const businessArea = useBusinessArea();
  return (
    <div>
      {menuItems.map((item) => {
        return (
          <ListItem
            button
            component={Link}
            key={item.name}
            to={`/${businessArea}${item.href}`}
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
