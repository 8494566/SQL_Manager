
// MFCAppManagerDlg.h : 头文件
//

#pragma once
#include "stdafx.h"

// CMFCAppManagerDlg 对话框
class CMFCAppManagerDlg : public CDialogEx
{
	// 构造
public:
	CMFCAppManagerDlg(CWnd* pParent = NULL);	// 标准构造函数

// 对话框数据
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_MFCAPPMANAGER_DIALOG };
#endif

protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV 支持


// 实现
protected:
	HICON m_hIcon;

	// 生成的消息映射函数
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()
public:
	bool m_start;
	bool m_binding;
public:
	_ConnectionPtr m_pConnection;//连接access数据库的链接对象  
	_RecordsetPtr m_pRecordset;//结果集对象
	_bstr_t m_sqlCmd;
	int m_point;
	int m_int_camp;
	int m_int_sex;
	int m_int_hold;
	int m_int_exp;
	int m_obj_id;
	int m_goodsnum;
	int m_new_objid;
public:
	CString m_name;
	CString m_cstring_point;
	CString m_explevel;
	CString m_new_name;
	BOOL m_camp;
	BOOL m_bool_sex;
	BOOL m_is_cpy;
	CString m_string_hold;
	CString m_string_exp;
	CString m_goodsbuf;
	CString m_ip_pont;
	CString m_world;
	CString m_reolid;
public:
	afx_msg void OnBnClickedButtonConnect();
	afx_msg BOOL CMFCAppManagerDlg::ExcuteCmd(CString bstrSqlCmd);
	afx_msg void OnEnChangeEditname();
	afx_msg void OnBnClickedButtonYes();
	afx_msg void OnEnChangeEditpoint();
	afx_msg void OnBnClickedButtonYesPoint();
	afx_msg void OnEnChangeStaticExplevel();
	afx_msg void OnBnClickedButtonYesExplevel();
	afx_msg void OnEnChangeEditnameNew();
	afx_msg void OnBnClickedButtonYesNewname();
	afx_msg void OnBnClickedButtonDelete();
	afx_msg void OnBnClickedCheckCamp();
	afx_msg void OnBnClickedButtonSetcomp();
	afx_msg void OnBnClickedCheckSex();
	afx_msg void OnBnClickedButtonSex();
	afx_msg void OnBnClickedButtonClanid();
	afx_msg void OnBnClickedButtonShopping();
	afx_msg void OnEnChangeEditpointHold();
	afx_msg void OnEnChangeEditpointexp();
	afx_msg void OnBnClickedButtonYesPointHold();
	afx_msg void OnBnClickedButtonHold();
	afx_msg void OnBnClickedButtonYesPointExp();
	afx_msg void OnBnClickedButton4Zs();
	afx_msg void OnBnClickedButton4Hy();
	afx_msg void OnBnClickedButton4Fs();
	afx_msg void OnBnClickedButton5Noe();
	afx_msg void OnBnClickedButton5Two();
	afx_msg void OnBnClickedButton5Cpy();
	afx_msg void OnBnClickedButton5Pas();
	afx_msg void OnEnChangeEditIpandpont();
	afx_msg void OnEnChangeEditWold();
	afx_msg void OnEnChangeEditpointZhuanyi();
	afx_msg void OnBnClickedButtonYesZhuanyi();
	afx_msg virtual BOOL PreTranslateMessage(MSG* pMsg);

	afx_msg void OnEnChangeEditnameObjid();
	CString m_str_bojid;
	afx_msg void OnBnClickedButtonYesBojid();
	CString m_clan_name;
	afx_msg void OnBnClickedButtonClan();
	afx_msg void OnEnChangeEditClanName();
	afx_msg void OnBnClickedButtonClanDelete();
	CString m_user_name;
	CString m_user_word;
	afx_msg void OnEnChangeEditpointUsername();
	afx_msg void OnEnChangeEditpointUserword();
	afx_msg void OnBnClickedButtonUaarOk();
	CString m_set_user_name;
	CString m_set_user_world;
	afx_msg void OnEnChangeEditpointUsernameSet();
	afx_msg void OnEnChangeEditpointUserwordset();
	afx_msg void OnBnClickedButtonUaarOk2();
	afx_msg void OnBnClickedButton2Hy();
	afx_msg void OnBnClickedButton2Zs();
	afx_msg void OnBnClickedButton2Fs();
};
