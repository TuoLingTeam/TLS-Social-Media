/**
 * Copyright (c) Andy Zhou. (https://github.com/iszhouhua)
 *
 * This source code is licensed under the GPL-3.0 license found in the
 * LICENSE file in the root directory of this source tree.
 */

export default defineBackground(() => {
    onMessage('openPopup', () => {
        return browser.action.openPopup();
    });

    onMessage('openTaskDialog', ({ data, sender }) => {
        return sendMessage('openTaskDialog', data, sender.tab?.id);
    });

    onMessage('fetch', async ({ data, sender }) => {
        try {
            if (!sender.tab?.id) {
                console.error('No tab ID available');
                return null;
            }
            
            console.log('Executing fetch in tab:', sender.tab.id, 'URL:', data.url);
            
            const results = await browser.scripting.executeScript({
                target: {
                    tabId: sender.tab.id
                },
                world: "MAIN",
                // @ts-ignore
                func: async (fetchData) => {
                    try {
                        console.log('Fetching in MAIN world:', fetchData.url);
                        const response = await window.fetch(fetchData.url, fetchData);
                        console.log('Response status:', response.status);
                        
                        if (!response.ok) {
                            console.error('Response not OK:', response.status, response.statusText);
                            return null;
                        }
                        
                        const data = await response.json();
                        console.log('Response data:', data);
                        return data;
                    } catch (err) {
                        console.error('Fetch error in MAIN world:', err);
                        return null;
                    }
                },
                args: [data]
            });
            
            const result = results?.[0]?.result;
            console.log('Execute script result:', result);
            
            if (!result) {
                console.error('Fetch failed: no result returned');
            }
            
            return result;
        } catch (error) {
            console.error('Execute script error:', error);
            return null;
        }
    });

    onMessage('webmsxyw', ({ data, sender }) => {
        return browser.scripting.executeScript({
            target: {
                tabId: sender.tab?.id!
            },
            world: "MAIN",
            func: (path, body) => {
                // @ts-ignore
                return window["_webmsxyw"](path, body ? JSON.parse(body) : undefined);
            },
            args: [data.path, data.body ? JSON.stringify(data.body) : '']

        }).then(res => res?.[0]?.result as any);
    });

    onMessage('mnsv2', ({ data, sender }) => {
        return browser.scripting.executeScript({
            target: {
                tabId: sender.tab?.id!
            },
            world: "MAIN",
            func: (a,b) => {
                // @ts-ignore
                return window["mnsv2"](a,b);
            },
            args: data

        }).then(res => res?.[0]?.result as any);
    });

    onMessage('download', ({ data }) => {
        return browser.downloads.download(data);
    });
});