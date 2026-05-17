// ==UserScript==
// @name         Moodswings Card Downloader
// @namespace    https://github.com/pixiv-script
// @version      1.0
// @description  Download all card images from a Moodswings spoiler page
// @match        https://magic.wizards.com/*
// @grant        GM_download
// @grant        GM_registerMenuCommand
// ==/UserScript==

(function () {
  "use strict";

  function buildLabelMap() {
    const map = new Map();
    document.querySelectorAll("strong").forEach((el) => {
      const text = el.textContent.trim();
      const match = text.match(/^(.+?)\s+\((.+)\)$/);
      if (match) map.set(match[1].trim(), text);
    });
    return map;
  }

  function downloadAllCards() {
    const cards = document.querySelectorAll("magic-card[face]");
    if (cards.length === 0) {
      alert("No cards found on this page");
      return;
    }

    const labelMap = buildLabelMap();

    const images = Array.from(cards).map((card) => {
      const caption = card.getAttribute("caption") || "";
      const label = labelMap.get(caption) || caption || card.getAttribute("face").split("/").pop().replace(/\.[^.]+$/, "");
      return {
        url: card.getAttribute("face"),
        name: label.replace(/[/\\?%*:|"<>]/g, "_") + ".webp",
      };
    });

    const total = images.length;
    let completed = 0;
    let failed = 0;
    const originalTitle = document.title;

    const updateTitle = () => {
      const done = completed + failed;
      if (done < total) {
        document.title = `[${done}/${total}] ${originalTitle}`;
      } else {
        document.title = failed > 0
          ? `[Done: ${completed} ok, ${failed} failed] ${originalTitle}`
          : `[Done: ${total}] ${originalTitle}`;
        setTimeout(() => { document.title = originalTitle; }, 5000);
      }
    };

    updateTitle();
    console.log(`Downloading ${total} card(s)...`);

    images.forEach(({ url, name }, index) => {
      setTimeout(() => {
        GM_download({
          url,
          name,
          headers: { Referer: "https://magic.wizards.com/" },
          onerror: (err) => {
            console.error(`Failed to download ${name}:`, err);
            failed++;
            updateTitle();
          },
          onload: () => {
            console.log(`Downloaded: ${name}`);
            completed++;
            updateTitle();
          },
        });
      }, index * 200);
    });
  }

  GM_registerMenuCommand("Download All Cards", downloadAllCards);

  document.addEventListener("keydown", (e) => {
    if (e.metaKey && e.altKey && e.code === "Period") {
      e.preventDefault();
      downloadAllCards();
    }
  });
})();
