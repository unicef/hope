import {
  Avatar,
  Button,
  ClickAwayListener,
  Grow,
  MenuItem,
  MenuList,
  Paper,
  Popper,
} from '@mui/material';
import styled from 'styled-components';
import React, { ReactElement, useState, useRef, useEffect } from 'react';

const UserProfileButton = styled(Button)`
  && {
    color: #e3e6e7;
  }
`;
const MenuButtonText = styled.span`
  margin-left: ${({ theme }) => theme.spacing(2)};
`;
interface UserProfileMenuProps {
  meData;
}
export function UserProfileMenu({
  meData,
}: UserProfileMenuProps): ReactElement {
  const [open, setOpen] = useState(false);
  const anchorRef = useRef<HTMLButtonElement>(null);
  // return focus to the button when we transitioned from !open -> open
  const prevOpen = useRef(open);
  useEffect(() => {
    if (prevOpen.current === true && open === false) {
      anchorRef.current?.focus();
    }

    prevOpen.current = open;
  }, [open]);

  const handleToggle = (): void => {
    setOpen((previousOpen) => !previousOpen);
  };

  const handleClearCache = () => {
    //TODO: Clear the cache from backend and frontend
  };

  const handleClose = (event): void => {
    if (
      anchorRef.current &&
      anchorRef.current.contains(event.target as HTMLElement)
    ) {
      return;
    }

    setOpen(false);
  };

  const handleLogout = (event: React.MouseEvent<HTMLAnchorElement>): void => {
    window.location.assign('/api/logout');
    localStorage.removeItem('AUTHENTICATED');
    handleClose(event);
    handleClearCache();
  };

  const handleClearCacheAndReloadWindow = () => {
    window.location.reload();
  };

  function handleListKeyDown(event: React.KeyboardEvent): void {
    if (event.key === 'Tab') {
      event.preventDefault();
      setOpen(false);
    }
  }
  if (!meData) {
    return null;
  }

  return (
    <>
      <UserProfileButton
        ref={anchorRef}
        onClick={handleToggle}
        data-cy="menu-user-profile"
      >
        <Avatar alt={meData.email} src="/static/images/avatar/1.jpg" />
        <MenuButtonText> {meData.email}</MenuButtonText>
      </UserProfileButton>
      <Popper
        open={open}
        anchorEl={anchorRef.current}
        role={undefined}
        transition
        disablePortal
      >
        {({ TransitionProps, placement }) => (
          <Grow
            {...TransitionProps}
            style={{
              transformOrigin:
                placement === 'bottom' ? 'center top' : 'center bottom',
            }}
          >
            <Paper>
              <ClickAwayListener onClickAway={handleClose}>
                <MenuList
                  component="ul"
                  autoFocusItem={open}
                  id="menu-list-grow"
                  onKeyDown={handleListKeyDown}
                >
                  <MenuItem
                    onClick={handleClearCacheAndReloadWindow}
                    data-cy="menu-item-clear-cache"
                  >
                    Clear Cache
                  </MenuItem>
                  <MenuItem
                    href="/api/logout"
                    onClick={handleLogout}
                    data-cy="menu-item-logout"
                  >
                    Logout
                  </MenuItem>
                </MenuList>
              </ClickAwayListener>
            </Paper>
          </Grow>
        )}
      </Popper>
    </>
  );
}
