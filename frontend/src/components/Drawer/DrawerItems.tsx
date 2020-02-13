import Collapse from '@material-ui/core/Collapse';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import React from 'react';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { menuItems } from './menuItems';

const Text = styled(ListItemText)`
  .MuiTypography-body1 {
    color: #233944;
    font-size: 14px;
    font-weight: 500;
    line-height: 16px;
  }
`;
const Icon = styled(ListItemIcon)`
  && {
    min-width: 0;
    padding-right: ${({ theme }) => theme.spacing(4)}px;
  }
`;

const SubList = styled(List)`
  padding-left: ${({ theme }) => theme.spacing(10)};
`;

interface Props {
  currentLocation: string;
}
export function DrawerItems({ currentLocation }: Props): React.ReactElement {
  const businessArea = useBusinessArea();
  const clearLocation = currentLocation.replace(`/${businessArea}`, '');
  const initialIndex = menuItems.findIndex((item) => {
    if (!item.secondaryActions) {
      return false;
    }
    return (
      item.secondaryActions.findIndex((secondaryItem) => {
        console.log(
          'Boolean(secondaryItem.selectedRegexp.exec(clearLocation)',
          Boolean(secondaryItem.selectedRegexp.exec(clearLocation)),
        );
        return Boolean(secondaryItem.selectedRegexp.exec(clearLocation));
      }) !== -1
    );
  });
  console.log('initialIndex', initialIndex);
  const [expandedItem, setExpandedItem] = React.useState(
    initialIndex !== -1 ? initialIndex : null,
  );
  console.log('clearLocation', clearLocation);

  return (
    <div>
      {menuItems.map((item, index) => {
        if (item.collapsable) {
          return (
            <>
              <ListItem
                button
                onClick={() =>
                  index === expandedItem
                    ? setExpandedItem(null)
                    : setExpandedItem(index)
                }
                component={Link}
                key={item.name}
              >
                <Icon>{item.icon}</Icon>
                <Text primary={item.name} />
                {expandedItem !== null && expandedItem === index ? (
                  <ExpandLess />
                ) : (
                  <ExpandMore />
                )}
              </ListItem>
              <Collapse in={expandedItem !== null && expandedItem === index}>
                <SubList component='div'>
                  {item.secondaryActions &&
                    item.secondaryActions.map((secondary) => (
                      <ListItem
                        button
                        component={Link}
                        key={secondary.name}
                        to={`/${businessArea}${secondary.href}`}
                        selected={Boolean(
                          secondary.selectedRegexp.exec(clearLocation),
                        )}
                      >
                        <Icon>{secondary.icon}</Icon>
                        <Text primary={secondary.name} />
                      </ListItem>
                    ))}
                </SubList>
              </Collapse>
            </>
          );
        }
        return (
          <ListItem
            button
            component={Link}
            key={item.name}
            to={`/${businessArea}${item.href}`}
            onClick={() => {
              setExpandedItem(null);
            }}
            selected={Boolean(item.selectedRegexp.exec(clearLocation))}
          >
            <Icon>{item.icon}</Icon>
            <Text primary={item.name} />
          </ListItem>
        );
      })}
    </div>
  );
}
