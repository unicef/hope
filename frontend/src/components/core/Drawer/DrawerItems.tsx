import { Box } from '@material-ui/core';
import Collapse from '@material-ui/core/Collapse';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import React from 'react';
import { Link, useHistory } from 'react-router-dom';
import styled from 'styled-components';
import {
  hasPermissionInModule,
  hasPermissions,
} from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useCashAssistUrlPrefixQuery } from '../../../__generated__/graphql';
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
  padding-left: ${({ theme }) => theme.spacing(10)}px !important;
`;

export const StyledLink = styled.a`
  color: #233944;
  font-size: 14px;
  font-weight: 500;
  line-height: 16px;
  text-decoration: none;
`;

interface Props {
  currentLocation: string;
}
export function DrawerItems({ currentLocation }: Props): React.ReactElement {
  const { data: cashAssistUrlData } = useCashAssistUrlPrefixQuery({
    fetchPolicy: 'cache-first',
  });
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const clearLocation = currentLocation.replace(`/${businessArea}`, '');
  const history = useHistory();
  const initialIndex = menuItems.findIndex((item) => {
    if (!item.secondaryActions) {
      return false;
    }
    return (
      item.secondaryActions.findIndex((secondaryItem) => {
        return Boolean(secondaryItem.selectedRegexp.exec(clearLocation));
      }) !== -1
    );
  });
  const [expandedItem, setExpandedItem] = React.useState(
    initialIndex !== -1 ? initialIndex : null,
  );
  if (permissions === null) return null;

  const cashAssistIndex = menuItems.findIndex(
    (item) => item.name === 'Payment Management',
  );

  menuItems[cashAssistIndex].href = cashAssistUrlData?.cashAssistUrlPrefix;

  const getInitialHrefForCollapsible = (secondaryActions): string => {
    let resultHref = '';
    for (const item of secondaryActions) {
      if (
        item.permissionModule &&
        hasPermissionInModule(item.permissionModule, permissions)
      ) {
        resultHref = item.href;
        break;
      }
    }
    return resultHref;
  };

  return (
    <div>
      {menuItems.map((item, index) => {
        if (
          item.permissionModule &&
          !hasPermissionInModule(item.permissionModule, permissions)
        )
          return null;

        if (item.permissions && !hasPermissions(item.permissions, permissions))
          return null;
        if (item.collapsable) {
          const hrefForCollapsibleItem = getInitialHrefForCollapsible(
            item.secondaryActions,
          );

          return (
            <div key={item.name + hrefForCollapsibleItem}>
              <ListItem
                button
                onClick={() => {
                  if (index === expandedItem) {
                    setExpandedItem(null);
                  } else {
                    setExpandedItem(index);
                  }
                  if (hrefForCollapsibleItem) {
                    history.push(`/${businessArea}${hrefForCollapsibleItem}`);
                  }
                }}
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
                    item.secondaryActions.map(
                      (secondary) =>
                        secondary.permissionModule &&
                        hasPermissionInModule(
                          secondary.permissionModule,
                          permissions,
                        ) && (
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
                        ),
                    )}
                </SubList>
              </Collapse>
            </div>
          );
        }
        return item.external ? (
          <ListItem button key={item.name + item.href}>
            <StyledLink target='_blank' href={item.href}>
              <Box display='flex'>
                <Icon>{item.icon}</Icon>
                <Text primary={item.name} />
              </Box>
            </StyledLink>
          </ListItem>
        ) : (
          <ListItem
            button
            component={Link}
            key={item.name + item.href}
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
