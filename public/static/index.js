const urlInput = document.getElementById("url-input");
const searchButton = document.getElementById("search-button");
const errorText = document.getElementById("error");
const loadingIndicator = document.getElementById("loading-indicator");

const resultsContainer = document.getElementById("result");
const voThumbnail = document.getElementById("vo-thumbnail");
const voTitle = document.getElementById("vo-title");
const voArtist = document.getElementById("vo-artist");
const voAlbum = document.getElementById("vo-album");
const voViews = document.getElementById("vo-views");
const voLikes = document.getElementById("vo-likes");

const convertButton = document.getElementById("convert-button");
const downloadButton = document.getElementById("download-button");

document.addEventListener("DOMContentLoaded", () => {
    searchButton.addEventListener("click", search);
});

async function search() {
    const url = urlInput.value;

    errorText.innerText = "";

    searchButton.disabled = true;
    loadingIndicator.style.display = "block";

    const response = await fetch("/search?url=" + encodeURIComponent(url));

    loadingIndicator.style.display = "none";
    searchButton.disabled = false;

    if (response.status !== 200) {
        errorText.innerText = await response.text();
        return;
    }

    const info = await response.json();

    voThumbnail.src = info.thumbnail || "";
    voTitle.innerText = info.title;
    voArtist.innerText = info.artist;
    voAlbum.innerText = info.album;
    voViews.innerText = `${info.view_count} Views`;
    voLikes.innerText = `${info.like_count} Likes`;

    convertButton.style.display = "block";
    downloadButton.style.display = "none";
    convertButton.addEventListener("click", async () => await convert(url));

    resultsContainer.style.display = "block";
}

async function convert(url) {
    searchButton.disabled = true;
    loadingIndicator.style.display = "block";

    const response = await fetch("/convert?url=" + encodeURIComponent(url));

    loadingIndicator.style.display = "none";
    searchButton.disabled = false;

    if (response.status !== 200) {
        errorText.innerHTML = "Failed to convert.";
        return;
    }

    const downloadPath = await response.text();

    downloadButton.href = downloadPath;
    downloadButton.download = true;

    convertButton.style.display = "none";
    downloadButton.style.display = "block";
}
