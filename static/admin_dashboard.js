// admin_dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const dashboardContainer = document.querySelector('.dashboard-container');
    const sidebar = document.querySelector('.sidebar');
    
    // Check if we should start with collapsed sidebar (mobile devices)
    function checkSidebarState() {
        if (window.innerWidth <= 992) {
            dashboardContainer.classList.add('sidebar-collapsed');
            sidebar.classList.remove('open');
        } else {
            // Restore from localStorage for desktop
            const sidebarState = localStorage.getItem('sidebarCollapsed');
            if (sidebarState === 'true') {
                dashboardContainer.classList.add('sidebar-collapsed');
            } else {
                dashboardContainer.classList.remove('sidebar-collapsed');
            }
        }
    }
    
    // Initialize sidebar state
    checkSidebarState();
    
    // Toggle sidebar on button click
    sidebarToggle.addEventListener('click', function() {
        if (window.innerWidth <= 992) {
            // For mobile: toggle open class
            sidebar.classList.toggle('open');
        } else {
            // For desktop: toggle collapsed state
            dashboardContainer.classList.toggle('sidebar-collapsed');
            // Save state to localStorage
            localStorage.setItem(
                'sidebarCollapsed', 
                dashboardContainer.classList.contains('sidebar-collapsed')
            );
        }
    });
    
    // Close sidebar on click outside (mobile only)
    document.addEventListener('click', function(event) {
        if (
            window.innerWidth <= 992 && 
            sidebar.classList.contains('open') && 
            !sidebar.contains(event.target) && 
            event.target !== sidebarToggle
        ) {
            sidebar.classList.remove('open');
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', checkSidebarState);
    
    // Navigation active state
    const currentLocation = window.location.href;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.href === currentLocation) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
    
    // Table row hover effect
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f9fafb';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
    
    // Action buttons tooltips
    const actionButtons = document.querySelectorAll('.btn-action');
    
    actionButtons.forEach(button => {
        // Simple tooltip functionality
        button.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.style.position = 'absolute';
            tooltip.style.backgroundColor = 'rgba(0,0,0,0.8)';
            tooltip.style.color = '#fff';
            tooltip.style.padding = '5px 10px';
            tooltip.style.borderRadius = '4px';
            tooltip.style.fontSize = '12px';
            tooltip.style.zIndex = '1000';
            
            // Determine tooltip text based on button class
            if (this.classList.contains('edit')) {
                tooltip.textContent = 'Edit';
            } else if (this.classList.contains('view')) {
                tooltip.textContent = 'View Details';
            } else if (this.classList.contains('delete')) {
                tooltip.textContent = 'Delete';
            }
            
            document.body.appendChild(tooltip);
            
            // Position the tooltip
            const rect = this.getBoundingClientRect();
            tooltip.style.top = `${rect.bottom + 5}px`;
            tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
            
            // Store tooltip element for removal
            this.tooltip = tooltip;
        });
        
        button.addEventListener('mouseleave', function() {
            if (this.tooltip) {
                document.body.removeChild(this.tooltip);
                this.tooltip = null;
            }
        });
    });
    
    // Export button functionality
    const exportButton = document.querySelector('.btn-outline');
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            alert('Export functionality will be implemented soon!');
        });
    }
    
    // Add New button functionality
    const addNewButton = document.querySelector('.btn-primary');
    if (addNewButton) {
        addNewButton.addEventListener('click', function() {
            // This would normally redirect to a create page
            alert('Add New functionality will be implemented soon!');
        });
    }
    
    // Simple animation for stats cards
    const statValues = document.querySelectorAll('.stat-value');
    
    // Animate counting up for stat values
    statValues.forEach(statValue => {
        const finalValue = statValue.textContent;
        const isCurrency = finalValue.includes('$');
        let value = 0;
        
        // Parse the numeric value
        let numericValue;
        if (isCurrency) {
            numericValue = parseFloat(finalValue.replace('$', ''));
        } else {
            numericValue = parseInt(finalValue);
        }
        
        // Skip animation for non-numeric values
        if (isNaN(numericValue)) return;
        
        // Determine increment
        const increment = Math.max(1, Math.floor(numericValue / 20));
        
        // Reset display value
        if (isCurrency) {
            statValue.textContent = '$0';
        } else {
            statValue.textContent = '0';
        }
        
        // Animate the count up
        const duration = 1500; // animation duration in ms
        const startTime = performance.now();
        
        function updateCount(currentTime) {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
            
            // Easing function for smoother animation
            const easeOutQuad = progress * (2 - progress);
            
            // Calculate current display value
            const currentValue = Math.floor(numericValue * easeOutQuad);
            
            // Update the text
            if (isCurrency) {
                statValue.textContent = `${currentValue.toFixed(2)}`;
            } else {
                statValue.textContent = currentValue;
            }
            
            // Continue animation if not complete
            if (progress < 1) {
                requestAnimationFrame(updateCount);
            } else {
                // Ensure final value is exact
                statValue.textContent = finalValue;
            }
        }
        
        // Start animation after a staggered delay
        setTimeout(() => {
            requestAnimationFrame(updateCount);
        }, 100);
    });
    
    // Data table filter and sort functionality
    const tableContainer = document.querySelector('.table-container');
    if (tableContainer) {
        // Add table search functionality
        const tableHeader = document.querySelector('.card-header');
        if (tableHeader) {
            // Create search input
            const searchContainer = document.createElement('div');
            searchContainer.className = 'search-container';
            searchContainer.style.marginTop = '10px';
            searchContainer.style.display = 'flex';
            searchContainer.style.alignItems = 'center';
            searchContainer.style.gap = '10px';
            
            const searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.placeholder = 'Search orders...';
            searchInput.style.padding = '0.5rem';
            searchInput.style.borderRadius = '4px';
            searchInput.style.border = '1px solid #e9ecef';
            searchInput.style.flex = '1';
            
            const searchButton = document.createElement('button');
            searchButton.className = 'btn btn-outline';
            searchButton.innerHTML = '<i class="bi bi-search"></i> Search';
            
            searchContainer.appendChild(searchInput);
            searchContainer.appendChild(searchButton);
            tableHeader.appendChild(searchContainer);
            
            // Search functionality
            function performSearch() {
                const searchTerm = searchInput.value.toLowerCase();
                const tableRows = document.querySelectorAll('.data-table tbody tr');
                
                tableRows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
            
            searchButton.addEventListener('click', performSearch);
            searchInput.addEventListener('keyup', function(event) {
                if (event.key === 'Enter') {
                    performSearch();
                }
            });
        }
        
        // Add sort functionality to table headers
        const tableHeaders = document.querySelectorAll('.data-table th');
        
        tableHeaders.forEach(header => {
            // Make headers look clickable
            header.style.cursor = 'pointer';
            header.style.userSelect = 'none';
            
            // Add sort icons
            const sortIcon = document.createElement('i');
            sortIcon.className = 'bi bi-arrow-down-up';
            sortIcon.style.fontSize = '0.8rem';
            sortIcon.style.marginLeft = '5px';
            sortIcon.style.opacity = '0.5';
            header.appendChild(sortIcon);
            
            // Sort direction state
            let sortDirection = 0; // 0: none, 1: asc, -1: desc
            
            header.addEventListener('click', function() {
                // Remove active sorting from all other headers
                tableHeaders.forEach(h => {
                    if (h !== header) {
                        h.lastElementChild.className = 'bi bi-arrow-down-up';
                        h.lastElementChild.style.opacity = '0.5';
                    }
                });
                
                // Update sort direction
                sortDirection = (sortDirection + 1) % 3 - 1; // Cycle through -1, 0, 1
                
                // Update sort icon
                if (sortDirection === 1) {
                    sortIcon.className = 'bi bi-sort-down-alt';
                    sortIcon.style.opacity = '1';
                } else if (sortDirection === -1) {
                    sortIcon.className = 'bi bi-sort-up';
                    sortIcon.style.opacity = '1';
                } else {
                    sortIcon.className = 'bi bi-arrow-down-up';
                    sortIcon.style.opacity = '0.5';
                }
                
                // Get column index
                const columnIndex = Array.from(header.parentElement.children).indexOf(header);
                
                // Sort the table
                const tableBody = document.querySelector('.data-table tbody');
                const rows = Array.from(tableBody.querySelectorAll('tr'));
                
                if (sortDirection !== 0) {
                    rows.sort((a, b) => {
                        const aValue = a.children[columnIndex].textContent.trim();
                        const bValue = b.children[columnIndex].textContent.trim();
                        
                        // Check if values are numeric (like for Order ID, Amount)
                        if (!isNaN(aValue.replace(/[^0-9.-]+/g, '')) && !isNaN(bValue.replace(/[^0-9.-]+/g, ''))) {
                            return sortDirection * (parseFloat(aValue.replace(/[^0-9.-]+/g, '')) - parseFloat(bValue.replace(/[^0-9.-]+/g, '')));
                        }
                        
                        // Otherwise sort alphabetically
                        return sortDirection * aValue.localeCompare(bValue);
                    });
                    
                    // Reorder the rows
                    rows.forEach(row => tableBody.appendChild(row));
                }
            });
        });
    }
    
    // Theme toggle functionality (light/dark mode)
    const themeToggle = document.createElement('button');
    themeToggle.className = 'theme-toggle btn-icon';
    themeToggle.innerHTML = '<i class="bi bi-moon"></i>';
    themeToggle.style.marginLeft = 'auto';
    themeToggle.style.marginRight = '10px';
    
    // Insert before the first button in header actions
    const headerActions = document.querySelector('.header-actions');
    if (headerActions) {
        headerActions.insertBefore(themeToggle, headerActions.firstChild);
        
        // Check for saved theme preference
        let darkMode = localStorage.getItem('darkMode') === 'true';
        
        // Apply initial theme
        if (darkMode) {
            document.body.classList.add('dark-mode');
            themeToggle.innerHTML = '<i class="bi bi-sun"></i>';
        }
        
        // Toggle theme on click
        themeToggle.addEventListener('click', function() {
            darkMode = !darkMode;
            document.body.classList.toggle('dark-mode');
            themeToggle.innerHTML = darkMode ? '<i class="bi bi-sun"></i>' : '<i class="bi bi-moon"></i>';
            localStorage.setItem('darkMode', darkMode);
        });
    }
});