import os
import io
import json
import uuid
import shutil
import zipfile
import tempfile
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any

PROJECTS_DIR = "projects"

@dataclass
class Project:
    project_id: str
    title: str
    worldview: str
    asset_path: str     # [RENAMED] assets_dir → asset_path (일관성)
    ratio: str          # [NEW] 화면비 (9:16 or 16:9)
    created_at: str

class ProjectManager:
    def __init__(self):
        self.base_dir = PROJECTS_DIR
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _project_path(self, project_id: str) -> str:
        return os.path.join(PROJECTS_DIR, project_id)

    def _load_json(self, path: str) -> Dict[str, Any] | None:
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, path: str, data: Dict[str, Any]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def create_project(self, title: str, worldview: str, assets_dir: str, ratio: str) -> Project:
        """새 프로젝트 생성 (중복 처리 포함)"""

        # [Logic] 중복 제목 처리 (title (2), title (3)...)
        original_title = title
        counter = 2
        existing_titles = [p.title for p in self.list_projects()]

        while title in existing_titles:
            title = f"{original_title} ({counter})"
            counter += 1

        pid = f"prj_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_project = Project(
            project_id=pid,
            title=title,
            worldview=worldview,
            asset_path=assets_dir,  # [FIX] assets_dir → asset_path
            ratio=ratio,
            created_at=timestamp
        )

        # 폴더 생성
        project_path = os.path.join(PROJECTS_DIR, pid)
        if not os.path.exists(project_path):
            os.makedirs(project_path)

        self._save_project_meta(new_project)
        return new_project

    def delete_project(self, project_id):
        """[NEW] 프로젝트 삭제"""
        path = os.path.join(PROJECTS_DIR, project_id)
        if os.path.exists(path):
            shutil.rmtree(path) # 폴더째로 삭제
            return True
        return False

    def list_projects(self):
        projects = []
        if not os.path.exists(PROJECTS_DIR): return projects

        for dirname in os.listdir(PROJECTS_DIR):
            meta_path = os.path.join(PROJECTS_DIR, dirname, "metadata.json")
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        proj = Project(
                            project_id=data.get("project_id"),
                            title=data.get("title"),
                            worldview=data.get("worldview"),
                            asset_path=data.get("asset_path") or data.get("assets_dir", "assets"),  # [FIX] 하위 호환
                            ratio=data.get("ratio", "9:16"), # 없으면 기본값
                            created_at=data.get("created_at", "")
                        )
                        projects.append(proj)
                except Exception as e:
                    print(f"Load Error {dirname}: {e}")

        projects.sort(key=lambda x: x.created_at or "", reverse=True)
        return projects

    def _save_project_meta(self, project: Project):
        path = os.path.join(PROJECTS_DIR, project.project_id, "metadata.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(project), f, ensure_ascii=False, indent=4)

    def update_worldview(self, project_id: str, worldview: str) -> bool:
        """프로젝트 metadata.json의 worldview를 업데이트한다."""
        pid = str(project_id or "").strip()
        if not pid:
            return False
        path = os.path.join(PROJECTS_DIR, pid, "metadata.json")
        metadata = self._load_json(path) or {}
        if not isinstance(metadata, dict):
            return False
        metadata["worldview"] = str(worldview or "")
        try:
            self._write_json(path, metadata)
        except Exception:
            return False
        return True

    def save_series_plan(self, project_id, plan_data):
        path = os.path.join(PROJECTS_DIR, project_id, "series_plan.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(plan_data, f, ensure_ascii=False, indent=4)

    def load_series_plan(self, project_id):
        path = os.path.join(PROJECTS_DIR, project_id, "series_plan.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def save_episode_detail(self, project_id, episode_no, detail_data):
        filename = f"ep_{episode_no}.json"
        path = os.path.join(PROJECTS_DIR, project_id, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(detail_data, f, ensure_ascii=False, indent=4)

    def load_episode_detail(self, project_id, episode_no):
        path = os.path.join(PROJECTS_DIR, project_id, f"ep_{episode_no}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    # ------------------------------------------------------------------
    # Backup & Restore utilities
    # ------------------------------------------------------------------
    def archive_project_to_zip(self, project_id: str) -> bytes:
        project_path = self._project_path(project_id)
        if not os.path.isdir(project_path):
            raise FileNotFoundError(f"Project path not found: {project_id}")

        metadata = self._load_json(os.path.join(project_path, "metadata.json")) or {}
        series_plan = self._load_json(os.path.join(project_path, "series_plan.json"))

        original_asset_path = metadata.get("asset_path")
        asset_inside_project = False
        if original_asset_path:
            try:
                asset_inside_project = os.path.commonpath([
                    os.path.abspath(original_asset_path),
                    os.path.abspath(project_path)
                ]) == os.path.abspath(project_path)
            except ValueError:
                asset_inside_project = False
        backup_info = {
            "project_id": project_id,
            "created_at": datetime.now().isoformat(),
            "path_mapping": {
                "asset_path": {
                    "original": original_asset_path,
                    "archived": "./assets"
                }
            }
        }

        buffer = io.BytesIO()
        exclude_files = {"backup_info.json"}
        if metadata:
            exclude_files.add("metadata.json")
        if series_plan is not None:
            exclude_files.add("series_plan.json")
        episode_files = sorted(
            fname for fname in os.listdir(project_path)
            if fname.startswith("ep_") and fname.endswith(".json")
        )
        exclude_files.update(episode_files)

        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            # sanitized metadata
            if metadata:
                safe_metadata = metadata.copy()
                safe_metadata["asset_path"] = "./assets"
                zf.writestr(f"{project_id}/metadata.json", json.dumps(safe_metadata, ensure_ascii=False, indent=4))

            if series_plan is not None:
                zf.writestr(f"{project_id}/series_plan.json", json.dumps(series_plan, ensure_ascii=False, indent=4))

            # episode detail files with normalized local paths
            for fname in episode_files:
                detail = self._load_json(os.path.join(project_path, fname)) or {}
                if "cuts" in detail:
                    for cut in detail["cuts"]:
                        path_value = cut.get("local_path")
                        normalized = self._relative_local_path(path_value, project_path)
                        if normalized:
                            cut["local_path"] = normalized
                zf.writestr(f"{project_id}/{fname}", json.dumps(detail, ensure_ascii=False, indent=4))

            # add remaining files/folders
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    rel = os.path.relpath(os.path.join(root, file), project_path)
                    top_name = rel.split(os.sep, 1)[0]
                    if top_name in exclude_files or os.path.basename(rel) in exclude_files:
                        continue
                    arcname = os.path.join(project_id, rel).replace("\\", "/")
                    zf.write(os.path.join(root, file), arcname)

            # include assets directory (external)
            if original_asset_path and os.path.isdir(original_asset_path) and not asset_inside_project:
                for root, dirs, files in os.walk(original_asset_path):
                    rel_root = os.path.relpath(root, original_asset_path)
                    for file in files:
                        src = os.path.join(root, file)
                        rel_path = os.path.normpath(os.path.join("assets", rel_root, file)).replace("\\", "/")
                        arcname = f"{project_id}/{rel_path}".replace("//", "/")
                        zf.write(src, arcname)
            else:
                backup_info["path_mapping"]["asset_path"]["missing"] = True

            zf.writestr(f"{project_id}/backup_info.json", json.dumps(backup_info, ensure_ascii=False, indent=4))

        buffer.seek(0)
        return buffer.getvalue()

    def restore_project_from_zip(self, zip_file) -> str:
        if isinstance(zip_file, (str, os.PathLike)):
            with open(zip_file, "rb") as f:
                file_bytes = f.read()
        elif hasattr(zip_file, "read"):
            file_bytes = zip_file.read()
        else:
            file_bytes = zip_file

        if not isinstance(file_bytes, (bytes, bytearray)):
            raise TypeError("zip_file must be bytes, a path, or a file-like object")

        temp_buffer = io.BytesIO(file_bytes)

        with zipfile.ZipFile(temp_buffer) as zf:
            metadata_members = [name for name in zf.namelist() if name.endswith("metadata.json")]
            if not metadata_members:
                raise ValueError("Metadata file not found in archive")
            metadata = json.loads(zf.read(metadata_members[0]).decode("utf-8"))
            original_root = metadata_members[0].split("/")[0]
            desired_id = metadata.get("project_id", original_root)
            target_id = self._resolve_project_id(desired_id)
            final_path = self._project_path(target_id)

            with tempfile.TemporaryDirectory() as tmpdir:
                zf.extractall(tmpdir)
                extracted_root = os.path.join(tmpdir, original_root)
                shutil.copytree(extracted_root, final_path)
                backup_info_path = os.path.join(final_path, "backup_info.json")
                if os.path.exists(backup_info_path):
                    os.remove(backup_info_path)

        # path healing
        metadata_path = os.path.join(final_path, "metadata.json")
        metadata_data = self._load_json(metadata_path) or {}
        metadata_data["project_id"] = target_id
        asset_hint = metadata_data.get("asset_path") or metadata_data.get("assets_dir") or "assets"
        if os.path.isabs(asset_hint):
            rel_asset_dir = "assets"
        else:
            rel_asset_dir = asset_hint.replace("./", "").lstrip("/\\") or "assets"
        assets_dir = os.path.join(final_path, rel_asset_dir)
        os.makedirs(assets_dir, exist_ok=True)
        metadata_data["asset_path"] = os.path.abspath(assets_dir)
        self._write_json(metadata_path, metadata_data)

        for fname in os.listdir(final_path):
            if not fname.startswith("ep_") or not fname.endswith(".json"):
                continue
            detail_path = os.path.join(final_path, fname)
            detail = self._load_json(detail_path) or {}
            changed = False
            for cut in detail.get("cuts", []):
                lp = cut.get("local_path")
                normalized = self._restore_local_path(lp, target_id)
                if normalized and normalized != lp:
                    cut["local_path"] = normalized
                    changed = True
            if changed:
                self._write_json(detail_path, detail)

        return target_id

    # ------------------------------------------------------------------
    # Path helpers for archive/restore
    # ------------------------------------------------------------------
    def _relative_local_path(self, path_value: str | None, project_path: str) -> str | None:
        if not path_value:
            return None
        abs_project = os.path.abspath(project_path)
        abs_value = os.path.abspath(path_value) if os.path.isabs(path_value) else os.path.abspath(os.path.join(os.getcwd(), path_value))
        try:
            rel = os.path.relpath(abs_value, abs_project)
            return rel.replace("\\", "/")
        except ValueError:
            return path_value.replace("\\", "/")

    def _restore_local_path(self, stored_value: str | None, project_id: str) -> str | None:
        if not stored_value:
            return None
        cleaned = stored_value.replace("\\", "/")
        if cleaned.startswith("./"):
            cleaned = cleaned[2:]
        if cleaned.startswith("projects/"):
            parts = cleaned.split("/", 2)
            cleaned = parts[2] if len(parts) > 2 else ""
        normalized = os.path.join(PROJECTS_DIR, project_id, cleaned)
        return os.path.abspath(normalized)

    def _resolve_project_id(self, desired_id: str) -> str:
        target_id = desired_id
        counter = 1
        while os.path.exists(self._project_path(target_id)):
            target_id = f"{desired_id}_{counter}"
            counter += 1
        return target_id

    # ------------------------------------------------------------------
    # Episode list helpers (class methods)
    # ------------------------------------------------------------------
    def load_episodes(self, project_id):
        """에피소드 리스트(JSON)를 로드합니다."""
        target_path = os.path.join(self.base_dir, project_id, "episodes.json")
        if not os.path.exists(target_path):
            return []
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_episodes(self, project_id, episodes_data):
        """에피소드 리스트를 JSON으로 저장합니다."""
        print(f"🐛 [Debug] Saving episodes for {project_id}. Count: {len(episodes_data) if episodes_data is not None else 0}")
        try:
            project_dir = os.path.join(self.base_dir, project_id)
            os.makedirs(project_dir, exist_ok=True)
            target_path = os.path.join(project_dir, "episodes.json")

            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(episodes_data, f, ensure_ascii=False, indent=4)
            print("🐛 [Debug] Save successful!")
            return True
        except Exception as e:
            print(f"⚠️ [Error] Save failed: {e}")
            return False


# ========== Module-level helpers for episodes ==========
def load_episodes(project_id):
    """프로젝트의 에피소드 리스트를 로드합니다."""
    file_path = os.path.join("projects", project_id, "episodes.json")

    if not os.path.exists(file_path):
        return []  # 파일이 없으면 빈 리스트 반환

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if data is not None else []
    except Exception as e:
        print(f"⚠️ 에피소드 로드 실패: {e}")
        return []


def save_episodes(project_id, episodes_data):
    """에피소드 리스트를 JSON 파일로 저장합니다."""
    dir_path = os.path.join("projects", project_id)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, "episodes.json")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(episodes_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"⚠️ 에피소드 저장 실패: {e}")
        return False
