from domain.base import Base
from domain.TorrentFile import TorrentFile
from sqlalchemy import Column, Integer, TEXT, DATE, ForeignKey, String, TIMESTAMP
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime


class Episode(Base):
    __tablename__ = 'episodes'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4)
    bangumi_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('bangumi.id'), nullable=False)
    bgm_eps_id = Column(Integer, nullable=False)
    episode_no = Column(Integer, nullable=False)
    name = Column(TEXT, nullable=True)
    name_cn = Column(TEXT, nullable=True)
    duration = Column(String, nullable=True)
    airdate = Column(DATE, nullable=True)
    status = Column(Integer, nullable=False)
    create_time = Column(TIMESTAMP, default=datetime.now(), nullable=False)
    update_time = Column(TIMESTAMP, default=datetime.now(), nullable=False)

    bangumi = relationship('Bangumi', back_populates='episodes')

    torrent_files = relationship('TorrentFile', order_by=TorrentFile.episode_id, back_populates='episode',
                                 cascade='all, delete, delete-orphan')

    STATUS_NOT_DOWNLOADED = 0
    STATUS_DOWNLOADING = 1
    STATUS_DOWNLOADED = 2

