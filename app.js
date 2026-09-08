// Avii's YT Grabber Client-Side App
document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const urlInput = document.getElementById('urlInput');
  const pasteBtn = document.getElementById('pasteBtn');
  const grabBtn = document.getElementById('grabBtn');
  const grabSpinner = document.getElementById('grabSpinner');
  const errorBox = document.getElementById('errorBox');
  const resultCard = document.getElementById('resultCard');

  const videoThumb = document.getElementById('videoThumb');
  const videoDuration = document.getElementById('videoDuration');
  const videoTitle = document.getElementById('videoTitle');
  const videoChannel = document.getElementById('videoChannel');
  const videoViews = document.getElementById('videoViews');
  const videoDate = document.getElementById('videoDate');

  const videoFormatsGrid = document.getElementById('videoFormatsGrid');
  const audioFormatsGrid = document.getElementById('audioFormatsGrid');
  const downloadBtn = document.getElementById('downloadBtn');
  const downloadBtnText = document.getElementById('downloadBtnText');
  const downloadSpinner = document.getElementById('downloadSpinner');
  const downloadStatus = document.getElementById('downloadStatus');
  const statusMessage = document.getElementById('statusMessage');

  // Configure Backend API URL:
  // Can be overridden via ?api=https://your-backend.onrender.com or localStorage
  const urlParams = new URLSearchParams(window.location.search);
  const customApi = urlParams.get('api') || localStorage.getItem('YT_API_BACKEND') || '';
  const API_BASE = customApi ? customApi.replace(/\/$/, '') : window.location.origin;

  let currentVideoInfo = null;
  let selectedFormatOption = null;

  // Paste from clipboard
  pasteBtn.addEventListener('click', async () => {
    try {
      if (navigator.clipboard && navigator.clipboard.readText) {
        const text = await navigator.clipboard.readText();
        if (text) {
          urlInput.value = text.trim();
          showError(null);
        }
      } else {
        urlInput.focus();
      }
    } catch (e) {
      urlInput.focus();
    }
  });

  // Grab Video Info
  grabBtn.addEventListener('click', () => fetchVideoInfo());
  urlInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') fetchVideoInfo();
  });

  async function fetchVideoInfo() {
    const rawUrl = urlInput.value.trim();
    if (!rawUrl) {
      showError('Please paste a valid YouTube URL first.');
      return;
    }

    showError(null);
    resultCard.classList.add('hidden');
    selectedFormatOption = null;
    updateDownloadBtn();

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/info?url=${encodeURIComponent(rawUrl)}`);
      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to fetch video details.');
      }

      currentVideoInfo = data;
      renderVideoDetails(data);
    } catch (err) {
      showError(err.message || 'Network error: Could not connect to API server.');
    } finally {
      setLoading(false);
    }
  }

  function renderVideoDetails(data) {
    const info = data.video;
    videoTitle.textContent = info.title || 'YouTube Video';
    videoChannel.textContent = info.channel || 'Unknown Channel';
    videoDuration.textContent = info.duration_str || '--:--';
    videoViews.textContent = (info.views || 0).toLocaleString();
    videoDate.textContent = info.upload_date || 'N/A';
    videoThumb.src = info.thumbnail || 'https://via.placeholder.com/320x180?text=No+Thumbnail';

    // Clear grids
    videoFormatsGrid.innerHTML = '';
    audioFormatsGrid.innerHTML = '';

    const options = data.formats || [];

    // Filter video and audio options
    const videoOpts = options.filter(o => o.type === 'video');
    const audioOpts = options.filter(o => o.type === 'audio' || o.type === 'original_audio');

    // Populate video formats
    videoOpts.forEach((opt, idx) => {
      const pill = createFormatPill(opt, idx === 0);
      videoFormatsGrid.appendChild(pill);
      if (idx === 0) selectPill(opt, pill);
    });

    // Populate audio formats
    audioOpts.forEach(opt => {
      const pill = createFormatPill(opt, false);
      audioFormatsGrid.appendChild(pill);
    });

    resultCard.classList.remove('hidden');
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function createFormatPill(opt, isFirst) {
    const pill = document.createElement('div');
    pill.className = 'format-pill';

    const resEl = document.createElement('span');
    resEl.className = 'pill-res';
    resEl.textContent = opt.quality_tag || 'HD';

    const sizeEl = document.createElement('span');
    sizeEl.className = 'pill-size';
    sizeEl.textContent = opt.size_str ? `~${opt.size_str}` : '';

    const tagEl = document.createElement('span');
    tagEl.className = 'pill-tag';
    tagEl.textContent = opt.ext ? opt.ext.toUpperCase() : 'MP4';

    pill.appendChild(resEl);
    pill.appendChild(sizeEl);
    pill.appendChild(tagEl);

    pill.addEventListener('click', () => {
      selectPill(opt, pill);
    });

    return pill;
  }

  function selectPill(opt, pillEl) {
    document.querySelectorAll('.format-pill').forEach(p => p.classList.remove('selected'));
    pillEl.classList.add('selected');
    selectedFormatOption = opt;
    updateDownloadBtn();
  }

  function updateDownloadBtn() {
    if (!selectedFormatOption) {
      downloadBtn.disabled = true;
      downloadBtnText.textContent = 'SELECT A QUALITY ABOVE';
    } else {
      downloadBtn.disabled = false;
      const tag = selectedFormatOption.quality_tag || 'Selected';
      const ext = (selectedFormatOption.ext || 'MP4').toUpperCase();
      downloadBtnText.textContent = `DOWNLOAD ${tag} (${ext})`;
    }
  }

  // Trigger Download
  downloadBtn.addEventListener('click', async () => {
    if (!selectedFormatOption || !currentVideoInfo) return;

    const rawUrl = urlInput.value.trim();
    downloadBtn.disabled = true;
    downloadSpinner.classList.remove('hidden');
    downloadStatus.classList.remove('hidden');
    statusMessage.textContent = '🚀 Preparing & merging high-definition stream with FFmpeg...';

    // Construct download streaming endpoint
    const query = new URLSearchParams({
      url: rawUrl,
      type: selectedFormatOption.type || 'video',
      ext: selectedFormatOption.ext || 'mp4',
      height: selectedFormatOption.height || 0,
      audio_quality: selectedFormatOption.audio_quality || '192',
      title: currentVideoInfo.video.title || 'video'
    });

    const downloadUrl = `${API_BASE}/api/download?${query.toString()}`;

    try {
      // Trigger native browser file download
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', '');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      statusMessage.textContent = '⚡ Download started! Check your browser/phone notification bar.';
      setTimeout(() => {
        downloadSpinner.classList.add('hidden');
        downloadBtn.disabled = false;
      }, 3000);
    } catch (err) {
      statusMessage.textContent = `❌ Error: ${err.message}`;
      downloadSpinner.classList.add('hidden');
      downloadBtn.disabled = false;
    }
  });

  function setLoading(isLoading) {
    if (isLoading) {
      grabBtn.disabled = true;
      grabSpinner.classList.remove('hidden');
    } else {
      grabBtn.disabled = false;
      grabSpinner.classList.add('hidden');
    }
  }

  function showError(msg) {
    if (!msg) {
      errorBox.classList.add('hidden');
      errorBox.textContent = '';
    } else {
      errorBox.textContent = msg;
      errorBox.classList.remove('hidden');
    }
  }
});
